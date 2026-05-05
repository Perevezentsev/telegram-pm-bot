import sqlite3
import os
from datetime import datetime

DB_PATH = 'exhibitions.db'

def init_db():
    """Создаёт таблицу с правильной структурой"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Удаляем старую таблицу, если есть (чтобы избавиться от несоответствия колонок)
    cursor.execute('DROP TABLE IF EXISTS exhibitions')
    
    # Создаём новую с правильными колонками
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
    
    conn.commit()
    conn.close()
    print("✅ База данных пересоздана с правильной структурой")

def get_all_exhibitions():
    """Возвращает список всех выставок"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT title, location, date_start, date_end, description, url FROM exhibitions ORDER BY date_start')
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_exhibition(title, location, date_start, date_end, description='', url=''):
    """Добавляет новую выставку"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO exhibitions (title, location, date_start, date_end, description, url, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (title, location, date_start, date_end, description, url, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def clear_exhibitions():
    """Очищает таблицу"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM exhibitions')
    conn.commit()
    conn.close()