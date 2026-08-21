#!/usr/bin/env python3
"""Bot de Telegram con IA local (Ollama) para GitHub Actions.

Diseñado para ejecutarse en un workflow con cron (cada 10-15 min):
  1. Lee updates pendientes del bot (getUpdates).
  2. Filtra mensajes dirigidos al bot: menciones (@bot), respuestas a
     mensajes del bot, o el comando /ai <texto> en privado.
  3. Solo procesa mensajes de los últimos MAX_EDAD minutos (por si el
     workflow se retrasa) para evitar duplicados.
  4. Envía el texto al modelo local vía Ollama (localhost:11434).
  5. Responde citando el mensaje original y CONFIRMA los updates con una
     última llamada getUpdates(offset=max+1), que marca todo como leído
     EN EL SERVIDOR de Telegram. Así no hay estado que persistir ni
     commits a git que puedan chocar con otros workflows.

Sin variables de estado en el repo: cero conflictos con los demás
workflows que también hacen push a master.

Variables de entorno:
  BOT_TOKEN      token del bot (obligatorio)
  OLLAMA_MODEL   modelo a usar (default: qwen2.5:1.5b)
  OLLAMA_URL     URL de Ollama (default: http://localhost:11434)
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request

MAX_UPDATES = 20          # procesados como máximo por ejecución
MAX_RESPUESTA = 3500      # Telegram corta a 4096; margen de seguridad
MAX_EDAD = 15 * 60        # ignora mensajes con más de 15 min
SYSTEM_PROMPT = (
    "Eres un asistente útil en un canal de Telegram sobre programación e IA. "
    "Responde en español, de forma concisa (máximo 150 palabras), clara y "
    "directa. Si te preguntan código, incluye un ejemplo breve."
)


def _post(url: str, payload: dict, timeout: int = 30) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def tg(token: str, method: str, payload: dict) -> dict | None:
    try:
        res = _post(f"https://api.telegram.org/bot{token}/{method}", payload)
        return res.get("result") if res.get("ok") else None
    except Exception as exc:
        print(f"[warn] {method}: {exc}", flush=True)
        return None


def obtener_bot_info(token: str) -> tuple[int | None, str]:
    """Devuelve (bot_id, bot_username)."""
    me = tg(token, "getMe", {})
    if me:
        return me.get("id"), (me.get("username") or "").lower()
    return None, ""


def es_para_el_bot(msg: dict, bot_id: int | None, bot_user: str) -> bool:
    """True si el mensaje menciona al bot, responde a uno suyo o es /ai."""
    texto = msg.get("text") or msg.get("caption") or ""
    bajo = texto.lower()

    # Comando explícito /ai
    if bajo.startswith("/ai"):
        return True

    # Respuesta a un mensaje del propio bot
    reply = msg.get("reply_to_message") or {}
    if bot_id and (reply.get("from") or {}).get("id") == bot_id:
        return True

    # Mención @botusername
    if bot_user and f"@{bot_user}" in bajo:
        return True

    # Menciones declaradas en entidades (por si el texto difiere)
    for ent in msg.get("entities") or []:
        if ent.get("type") == "mention":
            frag = texto[ent["offset"]:ent["offset"] + ent["length"]]
            if frag.lower() == f"@{bot_user}":
                return True
    return False


def limpiar_texto(texto: str, bot_user: str) -> str:
    texto = texto.strip()
    if texto.lower().startswith("/ai"):
        texto = texto[3:].strip()
    return texto.replace(f"@{bot_user}", "").strip() or "Hola"


def preguntar_ollama(url: str, model: str, prompt: str) -> str | None:
    try:
        res = _post(f"{url}/api/generate", {
            "model": model,
            "prompt": prompt,
            "system": SYSTEM_PROMPT,
            "stream": False,
            "options": {"num_predict": 400, "temperature": 0.7},
        }, timeout=300)
        return (res.get("response") or "").strip()
    except Exception as exc:
        print(f"[error] ollama: {exc}", flush=True)
        return None


def main():
    token = os.environ.get("BOT_TOKEN")
    if not token:
        print("[fatal] BOT_TOKEN no definido", flush=True)
        sys.exit(1)

    model = os.environ.get("OLLAMA_MODEL", "qwen2.5:1.5b")
    url = os.environ.get("OLLAMA_URL", "http://localhost:11434")

    bot_id, bot_user = obtener_bot_info(token)
    print(f"[info] bot=@{bot_user} id={bot_id} modelo={model}", flush=True)

    updates = tg(token, "getUpdates", {
        "offset": 0,
        "limit": 100,
        "timeout": 0,
        "allowed_updates": ["message", "channel_post"],
    }) or []
    updates = updates[-MAX_UPDATES:]  # los más recientes

    ahora = time.time()
    respondidos = 0
    max_update_id = 0

    for upd in updates:
        max_update_id = max(max_update_id, upd["update_id"] + 1)
        msg = upd.get("message") or upd.get("channel_post")
        if not msg or not es_para_el_bot(msg, bot_id, bot_user):
            continue

        # Descartar mensajes demasiado viejos (workflow retrasado/acumulado)
        fecha = msg.get("date", 0)
        if fecha and ahora - fecha > MAX_EDAD:
            print(f"[skip] mensaje de {ahora - fecha:.0f}s de antigüedad",
                  flush=True)
            continue

        chat_id = (msg.get("chat") or {}).get("id")
        texto = limpiar_texto(msg.get("text") or "", bot_user)
        user = (msg.get("from") or {}).get("first_name", "")
        print(f"[msg] {user}: {texto[:80]}", flush=True)

        respuesta = preguntar_ollama(url, model, texto)
        if not respuesta:
            respuesta = "Vaya, ahora mismo no consigo pensar. Inténtalo luego."
        if len(respuesta) > MAX_RESPUESTA:
            respuesta = respuesta[:MAX_RESPUESTA - 3] + "..."

        payload = {"chat_id": chat_id, "text": respuesta}
        if msg.get("message_id"):
            payload["reply_to_message_id"] = msg["message_id"]
        if tg(token, "sendMessage", payload):
            respondidos += 1

    # Confirmar en el servidor de Telegram: los updates procesados se
    # marcan como leídos y no volverán a llegarnos. Sin estado local.
    if max_update_id:
        tg(token, "getUpdates", {"offset": max_update_id, "limit": 1,
                                 "timeout": 0})
    print(f"[done] {respondidos} respuestas enviadas "
          f"de {len(updates)} updates", flush=True)


if __name__ == "__main__":
    main()
