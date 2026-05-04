import logging
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from database import ExhibitionsDB
from dotenv import load_dotenv
import os

load_dotenv()

# Включаем логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Инициализируем базу данных
db = ExhibitionsDB('exhibitions.db')

# --- Flask приложение для health check (чтобы Koyeb не убивал бота) ---
flask_app = Flask('')

@flask_app.route('/')
def health_check():
    return "I'm alive!", 200

def run_webserver():
    """Запускает Flask-сервер на порту 8080 в отдельном потоке"""
    flask_app.run(host='0.0.0.0', port=8080, debug=False)

# --- Все обработчики команд бота (start, help, ping, exhibitions и т.д.) ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот с информацией о выставках в Эрмитаже и Русском музее.\n\n"
        "Доступные команды:\n"
        "/exhibitions - список текущих выставок\n"
        "/hermitage - только выставки Эрмитажа\n"
        "/rusmuseum - только выставки Русского музея\n"
        "/help - помощь\n"
        "/ping - проверка работы бота"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Я показываю актуальные выставки в главных музеях Петербурга.\n\n"
        "Команды:\n"
        "/exhibitions - все текущие выставки\n"
        "/hermitage - выставки Эрмитажа\n"
        "/rusmuseum - выставки Русского музея\n\n"
        "Данные обновляются ежедневно автоматически."
    )

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("pong!")

async def exhibitions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать все текущие выставки"""
    exhibitions = db.get_current_exhibitions()
    
    if not exhibitions:
        await update.message.reply_text("😔 Актуальных выставок пока нет. Данные обновляются ежедневно.")
        return
    
    message = "🎨 *Актуальные выставки:*\n\n"
    
    # Группируем по музеям
    hermitage = [e for e in exhibitions if e['museum'] == 'Эрмитаж']
    rusmuseum = [e for e in exhibitions if e['museum'] == 'Русский музей']
    
    if hermitage:
        message += "🏛 *Эрмитаж:*\n"
        for exh in hermitage:
            message += f"• *{exh['title']}*\n"
            message += f"  📅 {exh['start_date']} — {exh['end_date']}\n"
            if exh['venue']:
                message += f"  📍 {exh['venue']}\n"
            message += "\n"
    
    if rusmuseum:
        message += "🏰 *Русский музей:*\n"
        for exh in rusmuseum:
            message += f"• *{exh['title']}*\n"
            message += f"  📅 {exh['start_date']} — {exh['end_date']}\n"
            if exh['venue']:
                message += f"  📍 {exh['venue']}\n"
            message += "\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def hermitage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Только Эрмитаж"""
    exhibitions = db.get_exhibitions_by_museum('Эрмитаж')
    
    if not exhibitions:
        await update.message.reply_text("В Эрмитаже пока нет актуальных выставок")
        return
    
    message = "🏛 *Выставки Эрмитажа:*\n\n"
    for exh in exhibitions:
        message += f"• *{exh['title']}*\n"
        message += f"  📅 {exh['start_date']} — {exh['end_date']}\n"
        if exh['venue']:
            message += f"  📍 {exh['venue']}\n"
        message += "\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def rusmuseum(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Только Русский музей"""
    exhibitions = db.get_exhibitions_by_museum('Русский музей')
    
    if not exhibitions:
        await update.message.reply_text("В Русском музее пока нет актуальных выставок")
        return
    
    message = "🏰 *Выставки Русского музея:*\n\n"
    for exh in exhibitions:
        message += f"• *{exh['title']}*\n"
        message += f"  📅 {exh['start_date']} — {exh['end_date']}\n"
        if exh['venue']:
            message += f"  📍 {exh['venue']}\n"
        message += "\n"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Вы написали: {update.message.text}")

def main():
    # Запускаем веб-сервер для health check в отдельном потоке
    web_thread = Thread(target=run_webserver, daemon=True)
    web_thread.start()
    
    # Инициализируем приложение бота

    token = os.getenv('BOT_TOKEN')
    if not token:
        raise ValueError("BOT_TOKEN не найден в переменных окружения. Проверьте файл .env")
    
    application = Application.builder().token(token).build()  # Замените на ваш реальный токен
    
    # Регистрируем команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ping", ping))
    application.add_handler(CommandHandler("exhibitions", exhibitions))
    application.add_handler(CommandHandler("hermitage", hermitage))
    application.add_handler(CommandHandler("rusmuseum", rusmuseum))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    # Запускаем бота (этот вызов блокирует выполнение, пока бот работает)
    application.run_polling()

if __name__ == '__main__':
    main()