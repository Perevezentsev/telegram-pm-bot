import os
import logging
import sqlite3
import subprocess
from datetime import datetime
from telegram.ext import Application, CommandHandler

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    logging.error("BOT_TOKEN не найден!")
    exit(1)

def get_db_connection():
    return sqlite3.connect('exhibitions.db')

def init_db():
    """Создаёт таблицу если не существует"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exhibitions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            location TEXT,
            date_start TEXT,
            date_end TEXT,
            description TEXT,
            url TEXT,
            updated_at TEXT
        )
    ''')
    conn.commit()
    conn.close()
    logging.info("БД инициализирована")

async def start(update, context):
    await update.message.reply_text(
        "👋 Привет! Я бот для поиска выставок в Петербурге.\n"
        "Используй /help"
    )

async def help_command(update, context):
    await update.message.reply_text(
        "📋 Команды:\n"
        "/exhibitions - Актуальные выставки\n"
        "/check - Сколько выставок в базе\n"
        "/update - Обновить базу из Git\n"
        "/ping - Проверка работы"
    )

async def ping(update, context):
    await update.message.reply_text("pong!")

async def check(update, context):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM exhibitions")
        count = cursor.fetchone()[0]
        cursor.execute("SELECT updated_at FROM exhibitions ORDER BY updated_at DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        updated = row[0][:10] if row else "неизвестно"
        await update.message.reply_text(f"📊 В базе {count} выставок\n🕐 Обновлено: {updated}")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def exhibitions(update, context):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT title, location, date_start, date_end, url
            FROM exhibitions
            ORDER BY date_start
        """)
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            await update.message.reply_text("📭 Пока нет выставок")
            return

        text = "🎨 АКТУАЛЬНЫЕ ВЫСТАВКИ:\n\n"
        for row in rows:
            text += f"📌 {row[0]}\n"
            text += f"📍 {row[1]}\n"
            text += f"📅 {row[2]}"
            if row[3]:
                text += f" — {row[3]}"
            text += "\n"
            if row[4]:
                text += f"🔗 {row[4]}\n"
            text += "\n"

        if len(text) > 4000:
            text = text[:4000] + "..."

        await update.message.reply_text(text)
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def update_db(update, context):
    """Обновляет базу: git pull + парсер"""
    msg = await update.message.reply_text("🔄 Обновляю...")
    try:
        subprocess.run(['git', 'pull', 'origin', 'master'], capture_output=True, text=True)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM exhibitions")
        count = cursor.fetchone()[0]
        conn.close()
        await msg.edit_text(f"✅ Готово! В базе {count} выставок.\nОтправь /exhibitions")
    except Exception as e:
        await msg.edit_text(f"❌ Ошибка: {e}")

def main():
    init_db()

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("check", check))
    app.add_handler(CommandHandler("exhibitions", exhibitions))
    app.add_handler(CommandHandler("update", update_db))

    logging.info("Бот запущен")
    app.run_polling()

if __name__ == '__main__':
    main()
