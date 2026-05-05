import os
import logging
import sqlite3
from telegram.ext import Application, CommandHandler

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv('BOT_TOKEN')

if not TOKEN:
    logging.error("BOT_TOKEN не найден!")
    exit(1)

def get_db_connection():
    return sqlite3.connect('exhibitions.db')

async def start(update, context):
    await update.message.reply_text("👋 Привет! Я бот для поиска выставок.\nИспользуй /help")

async def help_command(update, context):
    await update.message.reply_text(
        "📋 Команды:\n"
        "/start - Запустить бота\n"
        "/help - Эта справка\n"
        "/ping - Проверка работы\n"
        "/exhibitions - Список выставок\n"
        "/check - Диагностика"
    )

async def ping(update, context):
    await update.message.reply_text("pong!")

async def check(update, context):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM exhibitions")
        count = cursor.fetchone()[0]
        conn.close()
        await update.message.reply_text(f"📊 В базе {count} выставок")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def exhibitions(update, context):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT title, location, date_start, date_end, description FROM exhibitions LIMIT 10")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            await update.message.reply_text("📭 Пока нет выставок")
            return
        
        text = "🎨 ВЫСТАВКИ:\n\n"
        for row in rows:
            text += f"📌 {row[0]}\n"
            text += f"📍 {row[1]}\n"
            text += f"📅 {row[2]}\n"
            if row[3]:
                text += f"📅 до {row[3]}\n"
            text += "\n"
        
        if len(text) > 4000:
            text = text[:4000] + "..."
        
        await update.message.reply_text(text)
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def update_db(update, context):
    """Принудительное обновление базы данных из Git"""
    import subprocess
    import sqlite3
    from datetime import datetime
    
    msg = await update.message.reply_text("🔄 Обновляю базу данных...")
    
    try:
        # Тянем последнюю версию из Git
        subprocess.run(['git', 'pull', 'origin', 'master'], capture_output=True, text=True)
        
        # Переподключаемся к БД
        conn = sqlite3.connect('exhibitions.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM exhibitions")
        count = cursor.fetchone()[0]
        conn.close()
        
        await msg.edit_text(f"✅ База обновлена! В ней {count} выставок.\nОтправь /exhibitions")
    except Exception as e:
        await msg.edit_text(f"❌ Ошибка: {e}")

async def refresh_db(update, context):
    """Обновляет базу данных правильными выставками"""
    import sqlite3
    from datetime import datetime
    
    await update.message.reply_text("🔄 Обновляю базу данных...")
    
    try:
        conn = sqlite3.connect('exhibitions.db')
        cursor = conn.cursor()
        
        # Очищаем таблицу
        cursor.execute("DELETE FROM exhibitions")
        
        # Правильные данные о выставках
        exhibitions = [
            ("Шедевры импрессионистов", "Главный штаб, 4 этаж", "Постоянная экспозиция", "", "Моне, Ренуар, Дега, Сезанн, Ван Гог", ""),
            ("Сокровища сарматских вождей", "Зимний дворец, зал 26", "15 мая 2026", "15 сентября 2026", "Золотые украшения из сарматских курганов", ""),
            ("Древний Египет. Новые открытия", "Зимний дворец, залы 100-107", "1 апреля 2026", "30 ноября 2026", "Мумии, саркофаги, папирусы", ""),
            ("Кустодиев. Русская провинция", "Меншиковский дворец", "20 мая 2026", "20 августа 2026", "Живопись и графика Кустодиева", ""),
            ("Ювелирное искусство России XIX века", "Зимний дворец, Галерея драгоценностей", "Постоянная экспозиция", "", "Фаберже и другие мастера", ""),
        ]
        
        for ex in exhibitions:
            cursor.execute("""
                INSERT INTO exhibitions (title, location, date_start, date_end, description, url, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (*ex, datetime.now().isoformat()))
        
        conn.commit()
        cursor.execute("SELECT COUNT(*) FROM exhibitions")
        count = cursor.fetchone()[0]
        conn.close()
        
        await update.message.reply_text(f"✅ База обновлена! Добавлено {count} выставок.\nОтправь /exhibitions")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("check", check))
    app.add_handler(CommandHandler("exhibitions", exhibitions))
    app.add_handler(CommandHandler("update_db", update_db))
    app.add_handler(CommandHandler("refresh_db", refresh_db))
    
    logging.info("Бот запущен")
    app.run_polling()

if __name__ == '__main__':
    main()