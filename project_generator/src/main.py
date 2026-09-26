#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Project Generator - Generador automático de ideas de proyectos de software"""

import asyncio
import argparse
import sys
from pathlib import Path
from typing import List, Optional

# Añadir src al path
sys.path.insert(0, str(Path(__file__).parent))

from generator import ProjectGenerator, main as generator_main
from telegram_sender import send_to_telegram
from models import Nivel, Scope, Lenguaje, TipoProyecto
from config import settings
from ai_providers import QuotaExhaustedError


def parse_nivel(value: str) -> Nivel:
    try:
        return Nivel(value.lower())
    except ValueError:
        raise argparse.ArgumentTypeError(f"Nivel inválido: {value}. Use: junior, semisenior, senior")


def parse_scope(value: str) -> Scope:
    try:
        return Scope(value.lower())
    except ValueError:
        raise argparse.ArgumentTypeError(f"Scope inválido: {value}. Use: miniproyecto, proyecto, multiproyecto")


def parse_lenguaje(value: str) -> Lenguaje:
    try:
        return Lenguaje(value.lower())
    except ValueError:
        raise argparse.ArgumentTypeError(f"Lenguaje inválido: {value}. Use: python, javascript, typescript, csharp, go, rust")


def parse_tipo(value: str) -> TipoProyecto:
    try:
        return TipoProyecto(value.lower())
    except ValueError:
        raise argparse.ArgumentTypeError(f"Tipo inválido: {value}. Use: web, api, cli, mobile, desktop, fullstack, microservicio, bot, ia_ml, datos, devops, testing, seguridad")


async def cmd_generate(args):
    """Genera nuevos proyectos"""
    generator = ProjectGenerator()
    
    preferred_levels = [parse_nivel(args.nivel)] if args.nivel else None
    preferred_scopes = [parse_scope(args.scope)] if args.scope else None
    preferred_languages = [parse_lenguaje(args.lenguaje)] if args.lenguaje else None
    preferred_types = [parse_tipo(args.tipo)] if args.tipo else None
    
    try:
        projects = await generator.generate_projects(
            count=args.count,
            preferred_levels=preferred_levels,
            preferred_scopes=preferred_scopes,
            preferred_languages=preferred_languages,
            preferred_types=preferred_types
        )
    except QuotaExhaustedError as e:
        # Un tope de cuota es una condición del plan, no un defecto del código:
        # se avisa pero no se tumba el job, que quedaría rojo cada 4 horas de
        # forma permanente. La anotación aparece en la UI de Actions.
        print(f"\n[!] {e}")
        print("::warning::Cuota diaria de Gemini agotada: ejecución omitida, "
              "historial sin cambios y sin envío a Telegram.")
        return []
    
    if args.send_telegram and projects:
        print(f"\n[*] Enviando {len(projects)} proyectos a Telegram...")
        provider_name = projects[0].metadata.get("provider")
        success = await send_to_telegram(projects, provider_name=provider_name)
        if success:
            print("[✓] Enviado correctamente a Telegram")
        else:
            print("[✗] Error enviando a Telegram")
            sys.exit(1)
    
    return projects


async def cmd_history(args):
    """Muestra historial de proyectos generados"""
    generator = ProjectGenerator()
    history = generator.history
    
    print(f"\n📊 Historial de Proyectos")
    print(f"{'='*60}")
    print(f"Total generados: {history.total_generados}")
    print(f"Última generación: {history.fecha_ultima_generacion or 'Nunca'}")
    print(f"Proyectos en memoria: {len(history.proyectos)}")
    
    if args.list:
        for i, gp in enumerate(history.proyectos[-args.list:], 1):
            p = gp.proyecto
            print(f"\n{i}. {p.titulo} ({p.nivel.value} | {p.scope.value})")
            print(f"   💻 {p.tech_stack.lenguaje_principal.value} | 🏷️ {', '.join(t.value for t in p.tipo)}")
            print(f"   ⏱️ {p.tiempo_estimado_semanas} sem | 🆔 {p.id}")
            if args.verbose:
                print(f"   📝 {p.descripcion_corta}")
                print(f"   ⚡ {', '.join(p.funcionalidades_clave[:4])}")
    
    if args.stats:
        # Estadísticas
        from collections import Counter
        niveles = Counter(p.proyecto.nivel.value for p in history.proyectos)
        scopes = Counter(p.proyecto.scope.value for p in history.proyectos)
        lenguajes = Counter(p.proyecto.tech_stack.lenguaje_principal.value for p in history.proyectos)
        tipos = Counter(t.value for p in history.proyectos for t in p.proyecto.tipo)
        ia_count = sum(1 for p in history.proyectos if p.proyecto.cliente_ia_sugerido and p.proyecto.cliente_ia_sugerido != "none")
        
        print(f"\n📈 Estadísticas:")
        print(f"  Niveles: {dict(niveles)}")
        print(f"  Scopes: {dict(scopes)}")
        print(f"  Lenguajes: {dict(lenguajes)}")
        print(f"  Tipos: {dict(tipos)}")
        print(f"  Con IA: {ia_count}/{history.total_generados}")


async def cmd_send(args):
    """Envía proyectos existentes a Telegram"""
    generator = ProjectGenerator()
    history = generator.history
    
    if not history.proyectos:
        print("[!] No hay proyectos en el historial")
        return
    
    # Filtrar últimos N
    projects = history.proyectos[-args.count:] if args.count else history.proyectos
    
    print(f"[*] Enviando {len(projects)} proyectos a Telegram...")
    provider_name = projects[-1].metadata.get("provider")
    success = await send_to_telegram(projects, provider_name=provider_name)
    
    if success:
        print("[✓] Enviado correctamente")
    else:
        print("[✗] Error en el envío")
        sys.exit(1)


async def cmd_test_telegram(args):
    """Prueba la conexión a Telegram"""
    from telegram_sender import TelegramReporter
    
    reporter = TelegramReporter()
    try:
        await reporter.initialize()
        me = await reporter.bot.get_me()
        print(f"[✓] Bot conectado: @{me.username} (ID: {me.id})")
        
        # Enviar mensaje de prueba
        await reporter.bot.send_message(
            chat_id=settings.telegram_reports_channel_id,
            text="🧪 *Test de conexión* - Project Generator bot funcionando correctamente",
            parse_mode="Markdown"
        )
        print(f"[✓] Mensaje de prueba enviado al canal {settings.telegram_reports_channel_id}")
    except Exception as e:
        print(f"[✗] Error: {e}")
        sys.exit(1)


async def cmd_scrape(args):
    """Prueba los scrapers"""
    from scrapers import scrape_all_sources
    
    print("[*] Scrapeando fuentes externas...")
    ideas = await scrape_all_sources(settings.tuweb_dev_url, settings.tips_database_path)
    
    print(f"\n[✓] {len(ideas)} ideas encontradas:")
    for i, idea in enumerate(ideas[:10], 1):
        print(f"\n{i}. [{idea['fuente']}] {idea['titulo']}")
        print(f"   {idea['descripcion'][:150]}...")


async def cmd_quota(args):
    """Muestra el límite real de cuota de cada modelo de la cadena."""
    import quota as quota_mod

    modelos = None
    if args.modelos:
        modelos = [m.strip() for m in args.modelos.split(",") if m.strip()]
        print(f"[*] Sondeando: {', '.join(modelos)}")
    else:
        print(f"[*] Sondeando los modelos conocidos (usa --modelos para acotar)")
    print("[!] Cada sondeo gasta 1 petición del cupo diario de ese modelo.\n")

    resultados = await quota_mod.sondear_todos(settings.gemini_api_key, modelos)
    print(quota_mod.formatear(resultados))

    disponibles = [r for r in resultados if r.get("estado") == "disponible"]
    print(f"\n[*] {len(disponibles)}/{len(resultados)} modelos disponibles.")
    print("[*] El cupo es por proyecto y por modelo, así que suma entre modelos distintos.")


def main():
    parser = argparse.ArgumentParser(
        description="Project Generator - Generador automático de ideas de proyectos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python -m src.main generate --count 10
  python -m src.main generate --count 5 --nivel senior --scope multiproyecto --lenguaje python --send-telegram
  python -m src.main history --list 20 --stats
  python -m src.main send --count 5
  python -m src.main quota --modelos gemini-2.5-flash,gemini-2.5-flash-lite
  python -m src.main test-telegram
  python -m src.main scrape
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Generate
    gen_parser = subparsers.add_parser('generate', help='Generar nuevos proyectos')
    gen_parser.add_argument('--count', '-c', type=int, default=5, help='Número de proyectos a generar')
    gen_parser.add_argument('--nivel', choices=['junior', 'semisenior', 'senior'], help='Filtrar por nivel')
    gen_parser.add_argument('--scope', choices=['miniproyecto', 'proyecto', 'multiproyecto'], help='Filtrar por scope')
    gen_parser.add_argument('--lenguaje', choices=['python', 'javascript', 'typescript', 'csharp', 'go', 'rust'], help='Filtrar por lenguaje')
    gen_parser.add_argument('--tipo', choices=['web', 'api', 'cli', 'mobile', 'desktop', 'fullstack', 'microservicio', 'bot', 'ia_ml', 'datos', 'devops', 'testing', 'seguridad'], help='Filtrar por tipo')
    gen_parser.add_argument('--send-telegram', action='store_true', help='Enviar resultados a Telegram')
    gen_parser.set_defaults(func=cmd_generate)
    
    # History
    hist_parser = subparsers.add_parser('history', help='Ver historial de proyectos')
    hist_parser.add_argument('--list', '-l', type=int, metavar='N', help='Listar últimos N proyectos')
    hist_parser.add_argument('--stats', '-s', action='store_true', help='Mostrar estadísticas')
    hist_parser.add_argument('--verbose', '-v', action='store_true', help='Detalles completos')
    hist_parser.set_defaults(func=cmd_history)
    
    # Send
    send_parser = subparsers.add_parser('send', help='Enviar proyectos a Telegram')
    send_parser.add_argument('--count', '-c', type=int, help='Enviar últimos N proyectos (default: todos)')
    send_parser.set_defaults(func=cmd_send)
    
    # Test Telegram
    test_parser = subparsers.add_parser('test-telegram', help='Probar conexión Telegram')
    test_parser.set_defaults(func=cmd_test_telegram)
    
    # Scrape
    scrape_parser = subparsers.add_parser('scrape', help='Probar scrapers')
    scrape_parser.set_defaults(func=cmd_scrape)

    # Quota
    quota_parser = subparsers.add_parser(
        'quota',
        help='Ver el límite real de cuota de cada modelo (gasta 1 petición por modelo)'
    )
    quota_parser.add_argument('--modelos', help='Lista separada por comas (por defecto, los conocidos)')
    quota_parser.set_defaults(func=cmd_quota)


    args = parser.parse_args()
    
    # Ejecutar comando
    asyncio.run(args.func(args))


if __name__ == "__main__":
    main()