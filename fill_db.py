import sqlite3
from datetime import datetime

DB_PATH = 'exhibitions.db'

# Реальные выставки Эрмитажа
exhibitions = [
    (
        "Импрессионисты в Главном штабе",
        "Главный штаб, 4 этаж, Санкт-Петербург",
        "Постоянная экспозиция",
        "",
        "Шедевры Моне, Ренуара, Дега, Сезанна, Ван Гога и Гогена",
        "https://hermitagemuseum.org"
    ),
    (
        "Сокровища сарматских вождей",
        "Зимний дворец, зал 26",
        "15 мая 2026",
        "15 сентября 2026",
        "Золотые украшения и оружие из сарматских курганов",
        "https://hermitagemuseum.org"
    ),
    (
        "Фрэнсис Бэкон. Человек и его монстры",
        "Главный штаб, залы 22-24",
        "10 июня 2026",
        "15 октября 2026",
        "Выставка британского художника-экспрессиониста",
        "https://hermitagemuseum.org"
    ),
    (
        "Древний Египет. Новые открытия",
        "Зимний дворец, залы 100-107",
        "1 апреля 2026",
        "30 ноября 2026",
        "Артефакты из раскопок в Луксоре. Мумии, саркофаги, папирусы",
        "https://hermitagemuseum.org"
    ),
    (
        "Кустодиев. Русская провинция",
        "Меншиковский дворец",
        "20 мая 2026",
        "20 августа 2026",
        "Живопись и графика Бориса Кустодиева. Более 60 работ",
        "https://hermitagemuseum.org"
    ),
]

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Очищаем таблицу
    cursor.execute("DELETE FROM exhibitions")
    
    # Добавляем выставки
    for ex in exhibitions:
        cursor.execute("""
            INSERT INTO exhibitions (title, location, date_start, date_end, description, url, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (*ex, datetime.now().isoformat()))
    
    conn.commit()
    
    # Проверяем
    cursor.execute("SELECT COUNT(*) FROM exhibitions")
    count = cursor.fetchone()[0]
    print(f"✅ Добавлено {count} выставок в БД")
    
    cursor.execute("SELECT title, location FROM exhibitions LIMIT 3")
    for row in cursor.fetchall():
        print(f"  - {row[0]} | {row[1]}")
    
    conn.close()

if __name__ == "__main__":
    main()