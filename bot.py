import os
import logging
from telegram.ext import Application, CommandHandler

# Настройки
logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv('BOT_TOKEN')  # Bothost подставит из переменных окружения

# Проверка наличия токена
if not TOKEN:
    logging.error("BOT_TOKEN не найден! Добавьте переменную окружения в панели Bothost")
    exit(1)

# Обработчики команд
async def start(update, context):
    await update.message.reply_text("Бот работает!")

async def ping(update, context):
    await update.message.reply_text("pong!")

# Главная функция
def main():
    # Создаём приложение
    application = Application.builder().token(TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ping", ping))
    
    # Запускаем polling (не нужен SSL, работает везде)
    logging.info("Бот запущен в режиме polling")
    application.run_polling()

if __name__ == '__main__':
    main()