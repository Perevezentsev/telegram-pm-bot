import os
import logging
from telegram.ext import Application, CommandHandler
from database import init_db, get_all_exhibitions, add_exhibition, clear_exhibitions

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv('BOT_TOKEN')

if not TOKEN:
    logging.error("BOT_TOKEN не найден!")
    exit(1)

# Инициализируем БД при старте
init_db()

async def start(update, context):
    await update.message.reply_text("👋 Привет! Я бот для поиска выставок.\nИспользуй /help")

async def help_command(update, context):
    help_text = """
📋 *Команды:*
/start — Запустить бота
/help — Эта справка
/ping — Проверка работы
/exhibitions — Список выставок
/add_mock — Добавить тестовые выставки (для отладки)
/clear_mock — Очистить все выставки
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def ping(update, context):
    await update.message.reply_text("🏓 pong!")

async def exhibitions(update, context):
    rows = get_all_exhibitions()
    if not rows:
        await update.message.reply_text("📭 Пока нет активных выставок.")
        return
    
    text = "🎨 *Выставки:*\n\n"
    for row in rows[:10]:
        title, location, date_start, date_end, desc, url = row
        text += f"*{title}*\n📍 {location}\n📅 {date_start} – {date_end}\n\n"
    
    await update.message.reply_text(text, parse_mode="Markdown")

async def add_mock(update, context):
    """Добавляет тестовые выставки"""
    clear_exhibitions()
    
    test_data = [
        ("Импрессионисты в Русском музее", "Санкт-Петербург", "2026-05-10", "2026-06-15", "Великие импрессионисты: Моне, Ренуар, Дега", ""),
        ("Айвазовский. Морская стихия", "Третьяковская галерея", "2026-05-20", "2026-08-01", "Более 50 работ великого мариниста", ""),
        ("Современное искусство Китая", "ММОМА", "2026-05-01", "2026-07-20", "Выставка современных китайских художников", ""),
    ]
    
    for title, location, date_start, date_end, desc, url in test_data:
        add_exhibition(title, location, date_start, date_end, desc, url)
    
    await update.message.reply_text(f"✅ Добавлено {len(test_data)} тестовых выставок!\nОтправь /exhibitions чтобы увидеть.")

async def clear_mock(update, context):
    """Очищает все выставки"""
    clear_exhibitions()
    await update.message.reply_text("🗑️ Все выставки удалены из базы.")

def main():
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ping", ping))
    application.add_handler(CommandHandler("exhibitions", exhibitions))
    application.add_handler(CommandHandler("add_mock", add_mock))
    application.add_handler(CommandHandler("clear_mock", clear_mock))
    
    logging.info("🚀 Бот запущен")
    application.run_polling()

if __name__ == '__main__':
    main()