import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
import os

DB_PATH = 'exhibitions.db'

EXHIBITION_CATEGORIES = {'Выставка', 'Экспозиция'}

def init_db(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exhibitions (
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
    conn.commit()

def parse_rosphoto():
    print("🕷️ Парсим РОСФОТО...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    r = requests.get('https://www.rosphoto.org/events/', headers=headers, timeout=15)
    soup = BeautifulSoup(r.text, 'html.parser')

    exhibitions = []
    today = datetime.now()

    for row in soup.find_all('tr'):
        tds = row.find_all('td')
        if len(tds) < 4:
            continue

        dates_text = tds[0].get_text(strip=True)
        link = tds[1].find('a')
        category = tds[3].get_text(strip=True)

        if not link or category not in EXHIBITION_CATEGORIES:
            continue

        title = link.get_text(strip=True)
        url = link.get('href', '')

        parts = dates_text.split(' - ')
        date_start = parts[0].strip() if len(parts) >= 1 else ''
        date_end = parts[1].strip() if len(parts) >= 2 else date_start

        # Проверяем что выставка ещё не закончилась
        try:
            end_dt = datetime.strptime(date_end, '%d.%m.%Y')
            if end_dt < today:
                continue  # пропускаем прошедшие
            if end_dt.year < 2020:
                continue  # пропускаем сломанные даты
        except:
            continue  # пропускаем если дата не парсится

        exhibitions.append({
            'title': title,
            'location': 'РОСФОТО, Большая Морская, 35',
            'date_start': date_start,
            'date_end': date_end,
            'description': '',
            'url': url,
        })

    print(f"✅ Найдено {len(exhibitions)} актуальных выставок в РОСФОТО")
    return exhibitions

def save_to_db(exhibitions):
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM exhibitions')
    for ex in exhibitions:
        cursor.execute('''
            INSERT INTO exhibitions (title, location, date_start, date_end, description, url, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            ex['title'], ex['location'], ex['date_start'], ex['date_end'],
            ex['description'], ex['url'], datetime.now().isoformat()
        ))
    conn.commit()
    conn.close()
    print(f"💾 Сохранено {len(exhibitions)} выставок в БД")

def main():
    exhibitions = parse_rosphoto()
    save_to_db(exhibitions)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT title, date_start, date_end FROM exhibitions")
    for row in cursor.fetchall():
        print(f"  - {row[0]} | {row[1]} — {row[2]}")
    conn.close()

if __name__ == '__main__':
    main()
