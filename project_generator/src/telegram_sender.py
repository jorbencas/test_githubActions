import asyncio
import json
from typing import List, Optional
from datetime import datetime
from pathlib import Path

from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError
from telegram.helpers import escape_markdown

from models import ProyectoGenerado, Proyecto
from config import settings


def _esc(text: str) -> str:
    """Escapa texto dinámico para el modo Markdown legacy de Telegram.

    Sin esto, cualquier `_` (scikit_learn) o `*` en títulos y nombres de
    herramientas hace que Telegram rechace el mensaje entero.
    """
    return escape_markdown(str(text or ""))


class TelegramReporter:
    def __init__(self, provider_name: str = None):
        self.bot: Optional[Bot] = None
        self.channel_id = settings.telegram_reports_channel_id
        # El provider real usado se inyecta desde el generador (metadata de cada proyecto)
        self.provider_name = provider_name or f"gemini:{settings.ai_model}"
    
    async def initialize(self):
        if not self.bot:
            self.bot = Bot(token=settings.telegram_bot_token)
            # Verificar conexión
            me = await self.bot.get_me()
            print(f"[✓] Bot connected: @{me.username}")
    
    async def send_project_report(self, projects: List[ProyectoGenerado]) -> bool:
        if not projects:
            print("[~] No projects to send")
            return True
        
        await self.initialize()
        
        # Enviar resumen inicial
        summary = self._build_summary_message(projects)
        try:
            await self.bot.send_message(
                chat_id=self.channel_id,
                text=summary,
                parse_mode=ParseMode.MARKDOWN
            )
            print(f"[✓] Summary sent to channel {self.channel_id}")
        except TelegramError as e:
            print(f"[✗] Failed to send summary: {e}")
            return False
        
        # Enviar cada proyecto como mensaje separado (o en lote si son pocos)
        for i, gp in enumerate(projects, 1):
            p = gp.proyecto
            message = self._build_project_message(p, i, len(projects))
            
            try:
                await self.bot.send_message(
                    chat_id=self.channel_id,
                    text=message,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True
                )
                print(f"[✓] Project {i}/{len(projects)} sent: {p.titulo}")
                
                # Pequeña pausa para no hitrate limit
                if i < len(projects):
                    await asyncio.sleep(0.5)
                    
            except TelegramError as e:
                print(f"[✗] Failed to send project {p.titulo}: {e}")
                # Continuar con los siguientes
        
        # Enviar archivo JSON completo como documento
        await self._send_json_file(projects)
        
        return True
    
    def _build_summary_message(self, projects: List[ProyectoGenerado]) -> str:
        total = len(projects)
        niveles = {}
        scopes = {}
        lenguajes = {}
        tipos = {}
        con_ia = 0
        
        for gp in projects:
            p = gp.proyecto
            niveles[p.nivel.value] = niveles.get(p.nivel.value, 0) + 1
            scopes[p.scope.value] = scopes.get(p.scope.value, 0) + 1
            lang = p.tech_stack.lenguaje_principal.value
            lenguajes[lang] = lenguajes.get(lang, 0) + 1
            for t in p.tipo:
                tipos[t.value] = tipos.get(t.value, 0) + 1
            if p.cliente_ia_sugerido and p.cliente_ia_sugerido != "none":
                con_ia += 1
        
        msg = f"🚀 **Nuevos Proyectos Generados** — {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
        msg += f"📊 **Total:** {total} proyectos\n\n"
        
        msg += "📈 **Distribución:**\n"
        msg += f"  • Niveles: {', '.join(f'{_esc(k)}({v})' for k,v in sorted(niveles.items()))}\n"
        msg += f"  • Scopes: {', '.join(f'{_esc(k)}({v})' for k,v in sorted(scopes.items()))}\n"
        msg += f"  • Lenguajes: {', '.join(f'{_esc(k)}({v})' for k,v in sorted(lenguajes.items()))}\n"
        msg += f"  • Tipos: {', '.join(f'{_esc(k)}({v})' for k,v in sorted(tipos.items()))}\n"
        msg += f"  • Con IA: {con_ia}/{total}\n"
        
        msg += f"\n🤖 Generado con: `{self.provider_name}`\n"
        # La ruta va en code span: contiene '_' y Telegram lo rechazaría escapado o no fuera de ahí
        msg += f"🔗 Historial: `{settings.data_dir}/{settings.history_file}`"
        
        return msg
    
    def _build_project_message(self, p: Proyecto, index: int, total: int) -> str:
        msg = f"📋 **[{index}/{total}] {_esc(p.titulo)}**\n\n"
        msg += f"📝 {_esc(p.descripcion_corta)}\n\n"
        
        msg += f"🎯 **Nivel:** {_esc(p.nivel.value.title())} | **Scope:** {_esc(p.scope.value.title())}\n"
        msg += f"🏷️ **Tipos:** {', '.join(_esc(t.value) for t in p.tipo)}\n"
        msg += f"💻 **Lenguaje:** {_esc(p.tech_stack.lenguaje_principal.value)}\n\n"
        
        # Tech Stack resumido (Herramienta es un modelo Pydantic: acceso por atributo)
        stack_parts = []
        if p.tech_stack.frameworks:
            fw = [f"{_esc(f.nombre)} ({_esc((f.por_que or '')[:40])})" for f in p.tech_stack.frameworks[:3]]
            stack_parts.append(f"🔧 **Frameworks:** {', '.join(fw)}")
        if p.tech_stack.librerias:
            libs = [l.nombre for l in p.tech_stack.librerias[:4]]
            stack_parts.append(f"📚 **Libs:** {', '.join(_esc(x) for x in libs)}")
        if p.tech_stack.bases_datos:
            dbs = [d.nombre for d in p.tech_stack.bases_datos[:2]]
            stack_parts.append(f"🗄️ **BD:** {', '.join(_esc(x) for x in dbs)}")
        if p.tech_stack.ia_ml:
            ia = [i.nombre for i in p.tech_stack.ia_ml[:2]]
            stack_parts.append(f"🤖 **IA/ML:** {', '.join(_esc(x) for x in ia)}")
        
        if stack_parts:
            msg += "\n".join(stack_parts) + "\n\n"
        
        # Funcionalidades
        if p.funcionalidades_clave:
            funcs = p.funcionalidades_clave[:6]
            msg += f"⚡ **Funcionalidades:** {', '.join(_esc(f) for f in funcs)}\n"
        
        # IA
        if p.por_que_ia:
            msg += f"🧠 **IA:** {_esc(p.por_que_ia)} (`{_esc(p.cliente_ia_sugerido)}`)\n"
        
        # Estimaciones
        msg += f"⏱️ **Tiempo:** ~{p.tiempo_estimado_semanas} sem | **Complejidad:** {_esc(p.complejidad_estimada)}\n"
        
        # Prerequisitos clave
        if p.prerequisitos:
            msg += f"📋 **Requisitos:** {', '.join(_esc(r) for r in p.prerequisitos[:3])}\n"
        
        # Riesgos
        if p.riesgos:
            msg += f"⚠️ **Riesgos:** {', '.join(_esc(r) for r in p.riesgos[:2])}\n"
        
        # Fuente
        if p.fuente_inspiracion:
            msg += f"💡 **Fuente:** {_esc(p.fuente_inspiracion)}\n"
        msg += f"🆔 **ID:** `{_esc(p.id)}` | **Hash:** `{_esc(p.hash_unicidad)}`"
        
        return msg
    
    async def _send_json_file(self, projects: List[ProyectoGenerado]):
        """Envía el JSON completo como archivo adjunto"""
        import tempfile
        
        data = {
            "generated_at": datetime.now().isoformat(),
            "count": len(projects),
            "provider": self.provider_name,
            "projects": [gp.proyecto.model_dump(mode='json') for gp in projects]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                await self.bot.send_document(
                    chat_id=self.channel_id,
                    document=f,
                    filename=f"proyectos_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                    caption=f"📦 JSON completo con {len(projects)} proyectos generados"
                )
            print(f"[✓] JSON file sent")
        except TelegramError as e:
            print(f"[✗] Failed to send JSON: {e}")
        finally:
            Path(temp_path).unlink(missing_ok=True)


async def send_to_telegram(projects: List[ProyectoGenerado], provider_name: str = None) -> bool:
    """Función de conveniencia"""
    reporter = TelegramReporter(provider_name=provider_name)
    return await reporter.send_project_report(projects)