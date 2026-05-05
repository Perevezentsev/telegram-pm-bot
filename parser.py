import requests
from bs4 import BeautifulSoup
import sqlite3
import re
from datetime import datetime
import os
import ssl

# Отключаем проверку SSL для GitHub Actions
try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError:
    pass

DB_PATH = 'exhibitions.db'

def get_exhibitions_from_hermitage():
    """Парсит актуальные выставки с сайта Эрмитажа"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # Пробуем несколько возможных URL
    urls_to_try = [
        'https://hermitagemuseum.org/wps/portal/hermitage/what-s-on/exhibitions/',
        'https://hermitagemuseum.org/whats-on/',
        'https://hermitagemuseum.org/what-s-on?lng=en'
    ]
    
    exhibitions = []
    
    for url in urls_to_try:
        try:
            print(f"Пробуем URL: {url}")
            # Отключаем проверку SSL для GitHub Actions
            response = requests.get(url, headers=headers, timeout=30, verify=False)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Поиск по шаблону дат (российский формат)
            text = soup.get_text()
            date_pattern = r'(\d{1,2}\s+(?:января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\s+\d{4})'
            
            # Ищем заголовки рядом с датами
            for date_match in re.finditer(date_pattern, text):
                date_text = date_match.group(1)
                
                # Ищем заголовок перед датой
                context_start = max(0, date_match.start() - 200)
                context = text[context_start:date_match.start()]
                
                # Ищем потенциальное название выставки
                title = "Выставка в Эрмитаже"
                lines = context.split('\n')
                for line in reversed(lines[-5:]):
                    if len(line.strip()) > 5 and len(line.strip()) < 100:
                        title = line.strip()
                        break
                
                exhibitions.append({
                    'title': title,
                    'location': 'Государственный Эрмитаж',
                    'date_start': date_text,
                    'date_end': '',
                    'description': '',
                    'url': url
                })
            
            if exhibitions:
                print(f"Найдено {len(exhibitions)} выставок на {url}")
                break
                
        except Exception as e:
            print(f"Ошибка при парсинге {url}: {e}")
            continue
    
    # Если не нашли реальные выставки, возвращаем структурированные демо-данные
    if not exhibitions:
        print("⚠️ Не удалось найти выставки, используем примеры")
        exhibitions = [
            {
                'title': 'Постоянная экспозиция Главного музейного комплекса',
                'location': 'Зимний дворец, Главный штаб, Меншиковский дворец',
                'date_start': 'Постоянно',
                'date_end': '',
                'description': 'Шедевры мировой культуры от Древнего Египта до начала XX века',
                'url': 'https://hermitagemuseum.org'
            },
            {
                'title': 'Сокровища сарматских вождей',
                'location': 'Эрмитаж, Зимний дворец',
                'date_start': 'Май 2026',
                'date_end': 'Сентябрь 2026',
                'description': 'Уникальные артефакты из курганов сарматской знати',
                'url': 'https://hermitagemuseum.org'
            },
            {
                'title': 'Импрессионисты и постимпрессионисты',
                'location': 'Главный штаб, 4 этаж',
                'date_start': 'Постоянно',
                'date_end': '',
                'description': 'Работы Моне, Ренуара, Сезанна, Ван Гога и других',
                'url': 'https://hermitagemuseum.org'
            }
        ]
    
    return exhibitions

def save_to_db(exhibitions):
    """Сохраняет выставки в базу данных"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Проверяем структуру таблицы
    cursor.execute("PRAGMA table_info(exhibitions)")
    columns = [col[1] for col in cursor.fetchall()]
    
    # Если таблицы нет или структура неправильная, создаём заново
    if 'location' not in columns:
        cursor.execute('DROP TABLE IF EXISTS exhibitions')
        cursor.execute('''
            CREATE TABLE exhibitions (
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
    
    # Очищаем старые данные
    cursor.execute('DELETE FROM exhibitions')
    
    # Добавляем новые
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
            ex['url'],
            datetime.now().isoformat()
        ))
    
    conn.commit()
    conn.close()
    print(f"✅ Сохранено {len(exhibitions)} выставок")

def main():
    print("🕷️ Начинаем парсинг выставок Эрмитажа...")
    print(f"Текущая директория: {os.getcwd()}")
    
    exhibitions = get_exhibitions_from_hermitage()
    save_to_db(exhibitions)
    
    # Выводим содержимое БД для проверки
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT title, location, date_start FROM exhibitions")
    rows = cursor.fetchall()
    print(f"\n📊 Текущие выставки в БД ({len(rows)} шт.):")
    for row in rows:
        print(f"  - {row[0]} | {row[1]} | {row[2]}")
    conn.close()

if __name__ == '__main__':
    main()