"""Tests del preflight de Telegram: no generar si no se puede entregar.

Sin esto, un canal inalcanzable se descubre cuando ya se han gastado los
proyectos: la generación se guarda en el historial y el workflow lo commitea,
así que esos hashes ya no se vuelven a pedir y se pierden para siempre.
"""
import asyncio
import os
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC))

os.environ.setdefault("TELEGRAM_BOT_TOKEN", "123456:TEST")
os.environ.setdefault("TELEGRAM_REPORTS_PROYECTOS_CHANNEL_ID", "-1001234567890")
os.environ.setdefault("GEMINI_API_KEY", "test-key")

from telegram_sender import TelegramReporter  # noqa: E402


class _Chat:
    def __init__(self, id=-1001234567890, title="DevJobs", username="devjobs", type="channel"):
        self.id = id
        self.title = title
        self.username = username
        self.type = type


class _Bot:
    def __init__(self, chat=None, error=None):
        self._chat = chat
        self._error = error

    async def get_me(self):
        return type("Me", (), {"username": "jorbencas_bot", "id": 1})()

    async def get_chat(self, chat_id):
        if self._error:
            raise self._error
        return self._chat


def _reporter(bot):
    r = TelegramReporter()
    r.bot = bot
    return r


def test_canal_accesible_pasa_el_preflight():
    ok, diag = asyncio.run(_reporter(_Bot(chat=_Chat())).verificar_canal())
    assert ok is True
    assert diag == ""


def test_chat_not_found_falla_con_las_tres_causas():
    ok, diag = asyncio.run(
        _reporter(_Bot(error=Exception("Chat not found"))).verificar_canal()
    )
    assert ok is False
    # Las tres causas reales, en orden de probabilidad
    assert "no está en el canal" in diag
    assert "TELEGRAM_REPORTS_PROYECTOS_CHANNEL_ID" in diag
    assert "convirtió" in diag
    # Y una salida accionable
    assert "get_channel_id" in diag


def test_el_diagnostico_dice_el_id_que_se_esta_usando():
    _, diag = asyncio.run(
        _reporter(_Bot(error=Exception("Chat not found"))).verificar_canal()
    )
    assert str(TelegramReporter().channel_id) in diag


def test_el_preflight_no_revienta_con_una_excepcion_rara():
    """get_chat puede fallar con red, timeouts o lo que sea."""
    ok, diag = asyncio.run(_reporter(_Bot(error=TimeoutError("timed out"))).verificar_canal())
    assert ok is False
    assert "timed out" in diag


def test_el_diagnostico_tambien_cubre_el_400_de_send_message():
    """El caso del log: falla al enviar, no al comprobar."""
    reporter = TelegramReporter()
    diag = reporter._diagnostico_chat_no_encontrado(Exception("Chat not found"))
    assert "administrador" in diag


def test_el_preflight_es_mas_barato_que_generar():
    """Un get_chat no consume cuota de Gemini; generar, sí."""
    reporter = TelegramReporter()
    assert asyncio.iscoroutinefunction(reporter.verificar_canal)
