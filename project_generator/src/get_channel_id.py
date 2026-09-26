#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Obtener channel_id de un canal/grupo de Telegram.

Uso independiente - usa python-telegram-bot (Bot API) en lugar de Telethon.
"""
import asyncio
import sys
import os

# Añadir src al path para importar settings
sys.path.insert(0, str(os.path.dirname(__file__)))

from config import settings
from telegram import Bot


async def find_channel(target: str = None):
    bot = Bot(token=settings.telegram_bot_token)
    
    try:
        # Obtener info del bot
        me = await bot.get_me()
        print(f"[✓] Bot: @{me.username} (ID: {me.id})")
        
        # Intentar obtener info del canal configurado
        try:
            chat = await bot.get_chat(settings.telegram_reports_channel_id)
            print(f"\n[✓] Canal configurado encontrado:")
            print(f"    ID: {chat.id}")
            print(f"    Título: {chat.title}")
            print(f"    Tipo: {chat.type}")
            if chat.username:
                print(f"    Username: @{chat.username}")
            return
        except Exception as e:
            print(f"[!] No se pudo acceder al canal configurado: {e}")
        
        # Listar updates recientes para encontrar chats
        if target:
            print(f"\n[*] Buscando chats que contengan: '{target}'")
        else:
            print("\n[*] Buscando en updates recientes...")
        updates = await bot.get_updates(limit=100)
        
        seen = set()
        matches = []
        for update in updates:
            for msg_attr in ['message', 'edited_message', 'channel_post', 'edited_channel_post']:
                msg = getattr(update, msg_attr, None)
                if msg and msg.chat:
                    chat = msg.chat
                    key = (chat.id, chat.type)
                    if key not in seen:
                        seen.add(key)
                        title = getattr(chat, 'title', None) or getattr(chat, 'first_name', 'Sin título')
                        username = f"@{chat.username}" if chat.username else "sin username"
                        line = (f"  • ID: {chat.id:>15} | {chat.type:>12} | {title} ({username})")
                        if target and target in title.lower():
                            line += "  ← COINCIDENCIA"
                            matches.append(chat.id)
                        print(line)
        
        if not seen:
            print("  (No hay updates recientes. Envía un mensaje al bot o añádelo al canal)")
        elif target and not matches:
            print(f"  (Ningun chat coincide con '{target}')")
        elif matches:
            print(f"\n[✓] IDs que coinciden: {', '.join(str(m) for m in matches)}")
            
    except Exception as e:
        print(f"[✗] Error: {e}")
        sys.exit(1)


def main():
    if len(sys.argv) > 1:
        asyncio.run(find_channel(sys.argv[1].lower()))
    else:
        asyncio.run(find_channel())


if __name__ == "__main__":
    main()