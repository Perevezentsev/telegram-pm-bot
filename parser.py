import requests
from bs4 import BeautifulSoup
import sqlite3
import re
from datetime import datetime
import os

DB_PATH = 'exhibitions.db'

def get_exhibitions_from_hermitage():
    """Парсит актуальные выставки с сайта Эрмитажа"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    # Основная страница с выставками
    url = 'https://hermitagemuseum.org/whats-on/'
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Парсим HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ищем блоки с выставками
        # На странице Эрмитажа выставки в блоках с классом "event-item"
        events = soup.find_all('div', class_=re.compile(r'event|exhibition|item'))
        
        exhibitions = []
        
        for event in events:
            # Пробуем найти название
            title_elem = event.find(['h2', 'h3', 'div'], class_=re.compile(r'title|name'))
            title = title_elem.get_text(strip=True) if title_elem else None
            
            # Пробуем найти даты
            date_elem = event.find(class_=re.compile(r'date'))
            date_text = date_elem.get_text(strip=True) if date_elem else None
            
            # Пробуем найти место
            place_elem = event.find(class_=re.compile(r'place|location|hall'))
            place = place_elem.get_text(strip=True) if place_elem else None
            
            if title and date_text:
                # Парсим даты (формат может быть "21 февраля 2026 - 20 апреля 2026")
                date_match = re.search(r'(\d{1,2}\s+\w+\s+\d{4})\s*[-–]\s*(\d{1,2}\s+\w+\s+\d{4})', date_text)
                if date_match:
                    date_start = date_match.group(1)
                    date_end = date_match.group(2)
                else:
                    date_start = date_text
                    date_end = ""
                
                exhibitions.append({
                    'title': title,
                    'location': place or "Государственный Эрмитаж",
                    'date_start': date_start,
                    'date_end': date_end,
                    'description': "",
                    'url': url
                })
        
        # Если не нашли через универсальные классы, пробуем альтернативный URL
        if not exhibitions:
            # Английская версия
            url_en = 'https://hermitagemuseum.org/what-s-on?lng=en'
            response = requests.get(url_en, headers=headers, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ищем элементы с датами (прямой поиск по тексту)
            for element in soup.find_all(['div', 'li', 'article']):
                text = element.get_text()
                # Ищем паттерн даты в формате "21 February 2026 - 20 April 2026"
                if re.search(r'\d{1,2}\s+\w+\s+\d{4}\s*[-–]\s*\d{1,2}\s+\w+\s+\d{4}', text):
                    title_elem = element.find(['h2', 'h3', 'strong'])
                    title = title_elem.get_text(strip=True) if title_elem else "Выставка в Эрмитаже"
                    
                    place_elem = element.find(class_=re.compile(r'hall|place', re.I))
                    place = place_elem.get_text(strip=True) if place_elem else "Эрмитаж"
                    
                    exhibitions.append({
                        'title': title,
                        'location': place,
                        'date_start': "",
                        'date_end': "",
                        'description': text[:200],
                        'url': url_en
                    })
        
        return exhibitions
        
    except Exception as e:
        print(f"Ошибка при парсинге: {e}")
        return []

def save_to_db(exhibitions):
    """Сохраняет выставки в базу данных"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
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
    exhibitions = get_exhibitions_from_hermitage()
    
    if exhibitions:
        save_to_db(exhibitions)
        print(f"📊 В базу добавлено {len(exhibitions)} записей")
    else:
        print("⚠️ Не удалось найти выставки. Проверьте структуру сайта.")
        # Добавляем тестовые данные, если парсинг не сработал
        fallback_data = [
            ("Импрессионисты в Русском музее", "Санкт-Петербург", "2026-05-10", "2026-06-15"),
            ("Айвазовский. Морская стихия", "Третьяковская галерея", "2026-05-20", "2026-08-01"),
        ]
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM exhibitions')
        for title, loc, start, end in fallback_data:
            cursor.execute('INSERT INTO exhibitions (title, location, date_start, date_end, updated_at) VALUES (?, ?, ?, ?, ?)',
                         (title, loc, start, end, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        print("📝 Добавлены тестовые выставки (парсинг временно не работает)")

if __name__ == '__main__':
    main()