import sqlite3
from datetime import datetime

DB_PATH = 'exhibitions.db'

# Нормальные данные о выставках Эрмитажа
exhibitions = [
    {
        'title': 'Шедевры импрессионистов',
        'location': 'Главный штаб, 4 этаж',
        'date_start': 'Постоянная экспозиция',
        'date_end': '',
        'description': 'Моне, Ренуар, Дега, Сезанн, Ван Гог, Гоген'
    },
    {
        'title': 'Сокровища сарматских вождей',
        'location': 'Зимний дворец, зал 26',
        'date_start': '15 мая 2026',
        'date_end': '15 сентября 2026',
        'description': 'Золотые украшения и оружие из сарматских курганов'
    },
    {
        'title': 'Древний Египет. Новые открытия',
        'location': 'Зимний дворец, залы 100-107',
        'date_start': '1 апреля 2026',
        'date_end': '30 ноября 2026',
        'description': 'Мумии, саркофаги, папирусы из раскопок в Луксоре'
    },
    {
        'title': 'Кустодиев. Русская провинция',
        'location': 'Меншиковский дворец',
        'date_start': '20 мая 2026',
        'date_end': '20 августа 2026',
        'description': 'Живопись и графика Бориса Кустодиева (более 60 работ)'
    },
    {
        'title': 'Ювелирное искусство России XIX века',
        'location': 'Зимний дворец, Галерея драгоценностей',
        'date_start': 'Постоянная экспозиция',
        'date_end': '',
        'description': 'Фаберже, Овчинников, Хлебников'
    },
]

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Очищаем таблицу
    cursor.execute("DELETE FROM exhibitions")
    
    # Добавляем новые данные
    for ex in exhibitions:
        cursor.execute('''
            INSERT INTO exhibitions (title, location, date_start, date_end, description, url, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            ex['title'],
            ex['location'],
            ex['date_start'],
            ex['date_end'],
            ex['description'],
            '',
            datetime.now().isoformat()
        ))
    
    conn.commit()
    
    # Проверяем
    cursor.execute("SELECT COUNT(*) FROM exhibitions")
    count = cursor.fetchone()[0]
    print(f"✅ Добавлено {count} выставок")
    
    # Показываем что добавили
    cursor.execute("SELECT title, location, date_start FROM exhibitions")
    for row in cursor.fetchall():
        print(f"  - {row[0]} | {row[1]} | {row[2]}")
    
    conn.close()

if __name__ == '__main__':
    main()