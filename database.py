import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

class ExhibitionsDB:
    def __init__(self, db_path="exhibitions.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Создает таблицу если её нет"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS exhibitions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    museum TEXT NOT NULL,
                    title TEXT NOT NULL,
                    start_date TEXT NOT NULL,
                    end_date TEXT NOT NULL,
                    venue TEXT,
                    url TEXT,
                    description TEXT,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            # Создаем индекс для быстрого поиска
            conn.execute('CREATE INDEX IF NOT EXISTS idx_dates ON exhibitions(start_date, end_date)')
    
    def save_exhibitions(self, exhibitions: List[Dict]):
        """Сохраняет список выставок (очищая устаревшие)"""
        with sqlite3.connect(self.db_path) as conn:
            # Очищаем таблицу перед обновлением (или можно обновлять по ID)
            conn.execute('DELETE FROM exhibitions')
            
            # Вставляем новые данные
            for exh in exhibitions:
                conn.execute('''
                    INSERT INTO exhibitions (museum, title, start_date, end_date, venue, url, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    exh['museum'],
                    exh['title'],
                    exh['start_date'],
                    exh['end_date'],
                    exh.get('venue', ''),
                    exh.get('url', ''),
                    exh.get('description', '')
                ))
    
    def get_current_exhibitions(self) -> List[Dict]:
        """Возвращает текущие и будущие выставки"""
        today = datetime.now().strftime('%Y-%m-%d')
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row  # Чтобы получать словари вместо кортежей
            cursor = conn.execute('''
                SELECT * FROM exhibitions 
                WHERE end_date >= ? 
                ORDER BY start_date ASC
            ''', (today,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_exhibitions_by_museum(self, museum: str) -> List[Dict]:
        """Фильтр по музею"""
        today = datetime.now().strftime('%Y-%m-%d')
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT * FROM exhibitions 
                WHERE museum = ? AND end_date >= ?
                ORDER BY start_date ASC
            ''', (museum, today))
            return [dict(row) for row in cursor.fetchall()]