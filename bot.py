import os
import logging
from telegram.ext import Application, CommandHandler

# Настройки
logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv('BOT_TOKEN')

# Проверка наличия токена
if not TOKEN:
    logging.error("BOT_TOKEN не найден! Добавьте переменную окружения в панели Bothost")
    exit(1)

# Команда /start
async def start(update, context):
    await update.message.reply_text(
        "👋 Привет! Я бот для поиска выставок.\n"
        "Используй /help чтобы увидеть все команды."
    )

# Команда /help
async def help_command(update, context):
    help_text = """
📋 *Доступные команды:*

/start — Запустить бота
/help — Показать эту справку
/ping — Проверить, работает ли бот
/exhibitions — Показать список выставок

🔧 *В разработке:*
/artists — Поиск по художникам
/museums — Выставки по музеям

_Бот обновляется, скоро добавим новые фичи!_
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")

# Команда /ping
async def ping(update, context):
    await update.message.reply_text("🏓 pong!")

# Команда /exhibitions
async def exhibitions(update, context):
    # Пока временные данные, потом подключим SQLite
    text = """
🎨 *Актуальные выставки:*

1️⃣ *Импрессионисты в Русском музее*
   📍 Санкт-Петербург, до 15.06.2026

2️⃣ *Айвазовский. Морская стихия*
   📍 Третьяковская галерея, до 01.08.2026

3️⃣ *Современное искусство Китая*
   📍 ММОМА, до 20.07.2026

ℹ️ *Подробнее:* напиши /artists или /museums
"""
    await update.message.reply_text(text, parse_mode="Markdown")

# Главная функция
def main():
    application = Application.builder().token(TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ping", ping))
    application.add_handler(CommandHandler("exhibitions", exhibitions))
    
    logging.info("Бот запущен в режиме polling")
    application.run_polling()

if __name__ == '__main__':
    main()