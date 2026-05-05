import os
import logging
from telegram.ext import Application, CommandHandler
from database import init_db, get_all_exhibitions

# Настройки
logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv('BOT_TOKEN')

if not TOKEN:
    logging.error("BOT_TOKEN не найден!")
    exit(1)

# Инициализируем БД при старте
init_db()

async def start(update, context):
    await update.message.reply_text(
        "👋 Привет! Я бот для поиска выставок.\n"
        "Используй /help чтобы увидеть все команды."
    )

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
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def ping(update, context):
    """Диагностика вместо ping"""
    import os
    from database import get_all_exhibitions
    
    # Проверяем файл БД
    db_path = 'exhibitions.db'
    db_exists = os.path.exists(db_path)
    
    # Пробуем получить данные
    try:
        rows = get_all_exhibitions()
        rows_count = len(rows)
    except Exception as e:
        rows_count = f"Ошибка: {e}"
    
    # Список зарегистрированных команд
    commands_list = [cmd for cmd in context.application.handlers.get(0, [])]
    
    message = f"""
📊 *Диагностика*

БД файл: {'✅ есть' if db_exists else '❌ нет'}
Записей в БД: {rows_count}
Зарегистрировано команд: {len(commands_list)}

*Текущие команды:*
"""
    for handler in commands_list:
        if hasattr(handler, 'commands'):
            message += f"- /{handler.commands[0]}\n"
    
    await update.message.reply_text(message, parse_mode="Markdown")

async def exhibitions(update, context):
    """Показывает выставки из базы данных"""
    rows = get_all_exhibitions()
    
    if not rows:
        await update.message.reply_text(
            "📭 Пока нет активных выставок.\n"
            "Скоро появятся, загляните позже!"
        )
        return
    
    # Формируем красивое сообщение
    text = "🎨 *Актуальные выставки:*\n\n"
    for row in rows:
        title, location, date_start, date_end, desc, url = row
        text += f"*{title}*\n"
        text += f"📍 {location}\n"
        text += f"📅 {date_start} — {date_end}\n"
        if desc:
            text += f"📝 {desc[:100]}...\n"
        if url:
            text += f"🔗 [Подробнее]({url})\n"
        text += "\n"
    
    # Telegram имеет лимит на длину сообщения
    if len(text) > 4000:
        text = text[:4000] + "...\n\n_Слишком много выставок, сократил список_"
    
    await update.message.reply_text(text, parse_mode="Markdown")

# Добавьте эту функцию перед main()
async def check_db(update, context):
    """Диагностическая команда для проверки БД"""
    import os
    from database import get_all_exhibitions, init_db
    
    # Проверяем, существует ли файл БД
    db_exists = os.path.exists('exhibitions.db')
    
    # Пытаемся получить данные
    rows = get_all_exhibitions()
    
    message = f"""
📊 *Диагностика БД:*

Файл exhibitions.db: {'✅ существует' if db_exists else '❌ не найден'}
Количество записей: {len(rows)}

*Первые 3 записи (если есть):*
"""
    for i, row in enumerate(rows[:3]):
        title, location, date_start, date_end, desc, url = row
        message += f"\n{i+1}. {title} — {location} ({date_start}–{date_end})"
    
    if not rows:
        message += "\n\n⚠️ База данных пуста. Нужно добавить выставки через парсер или вручную."
    
    await update.message.reply_text(message, parse_mode="Markdown")


def main():
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ping", ping))
    application.add_handler(CommandHandler("exhibitions", exhibitions))
    application.add_handler(CommandHandler("check_db", check_db))
    
    logging.info("🚀 Бот запущен с SQLite")
    application.run_polling()

if __name__ == '__main__':
    main()