import os
import logging
from telegram.ext import Application, CommandHandler
from database import init_db, get_all_exhibitions, add_exhibition, clear_exhibitions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
TOKEN = os.getenv('BOT_TOKEN')

if not TOKEN:
    logger.error("BOT_TOKEN не найден!")
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
/add_mock — Добавить тестовые выставки
/clear_mock — Очистить все выставки
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def ping(update, context):
    await update.message.reply_text("🏓 pong!")

async def exhibitions(update, context):
    try:
        rows = get_all_exhibitions()
        if not rows:
            await update.message.reply_text("📭 Пока нет активных выставок.")
            return
        
        text = "🎨 *Выставки:*\n\n"
        for row in rows[:10]:
            title, location, date_start, date_end, desc, url = row
            text += f"*{title}*\n📍 {location}\n📅 {date_start} – {date_end}\n\n"
        
        await update.message.reply_text(text, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Ошибка в exhibitions: {e}")
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def add_mock(update, context):
    try:
        logger.info("Вызвана команда add_mock")
        clear_exhibitions()
        
        test_data = [
            ("Импрессионисты в Русском музее", "Санкт-Петербург", "2026-05-10", "2026-06-15", "Великие импрессионисты", ""),
            ("Айвазовский. Морская стихия", "Третьяковская галерея", "2026-05-20", "2026-08-01", "Более 50 работ", ""),
            ("Современное искусство Китая", "ММОМА", "2026-05-01", "2026-07-20", "Современные китайские художники", ""),
        ]
        
        for title, location, date_start, date_end, desc, url in test_data:
            add_exhibition(title, location, date_start, date_end, desc, url)
            logger.info(f"Добавлено: {title}")
        
        await update.message.reply_text(f"✅ Добавлено {len(test_data)} тестовых выставок!\nОтправь /exhibitions чтобы увидеть.")
    except Exception as e:
        logger.error(f"Ошибка в add_mock: {e}")
        await update.message.reply_text(f"❌ Ошибка при добавлении: {e}")

async def clear_mock(update, context):
    try:
        clear_exhibitions()
        await update.message.reply_text("🗑️ Все выставки удалены из базы.")
    except Exception as e:
        logger.error(f"Ошибка в clear_mock: {e}")
        await update.message.reply_text(f"❌ Ошибка при очистке: {e}")

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("exhibitions", exhibitions))
    app.add_handler(CommandHandler("add_mock", add_mock))
    app.add_handler(CommandHandler("clear_mock", clear_mock))
    
    logger.info("🚀 Бот запущен. Зарегистрированные команды: start, help, ping, exhibitions, add_mock, clear_mock")
    app.run_polling()

if __name__ == '__main__':
    main()