"""
Скрипт для ручного обновления выставок.

ИСПОЛЬЗОВАНИЕ:
  python update_exhibitions.py

Скрипт открывает exhibitions.json в текстовом редакторе.
Вы редактируете данные вручную и сохраняете.
Затем делаете git commit + git push — бот подхватит при следующем деплое.

Формат одной выставки в exhibitions.json:
{
    "title": "Название выставки",
    "location": "Здание, зал",
    "date_start": "апрель 2026",   // или "" если постоянная
    "date_end": "август 2026",     // или "" если постоянная
    "status": "current",           // current | permanent | upcoming | past
    "description": "Краткое описание",
    "url": "https://hermitagemuseum.org/..."
}
"""

import json
import os
import subprocess
from datetime import datetime

DATA_FILE = 'exhibitions.json'


def load():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save(data):
    data['updated_at'] = datetime.now().strftime('%Y-%m-%d')
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ Сохранено {len(data['exhibitions'])} выставок")


def show_current():
    data = load()
    print(f"\n📊 Текущие выставки ({len(data['exhibitions'])} шт.):")
    for i, ex in enumerate(data['exhibitions'], 1):
        status = ex.get('status', '?')
        print(f"  {i}. [{status}] {ex['title']}")
        if ex.get('date_start') or ex.get('date_end'):
            print(f"     📅 {ex.get('date_start','')} — {ex.get('date_end','')}")
    print(f"\n🕐 Обновлено: {data.get('updated_at', 'неизвестно')}")


def add_exhibition():
    print("\n➕ Добавление новой выставки")
    ex = {}
    ex['title'] = input("Название: ").strip()
    ex['location'] = input("Место (здание, зал): ").strip()
    ex['date_start'] = input("Начало (напр. 'май 2026', или Enter если постоянная): ").strip()
    ex['date_end'] = input("Конец (напр. 'август 2026', или Enter): ").strip()

    print("Статус: 1=текущая, 2=постоянная, 3=скоро, 4=прошедшая")
    status_map = {'1': 'current', '2': 'permanent', '3': 'upcoming', '4': 'past'}
    status_choice = input("Выберите (1-4): ").strip()
    ex['status'] = status_map.get(status_choice, 'current')

    ex['description'] = input("Описание (кратко): ").strip()
    ex['url'] = input("Ссылка (или Enter): ").strip()

    data = load()
    data['exhibitions'].append(ex)
    save(data)
    print(f"✅ Выставка '{ex['title']}' добавлена!")


def remove_exhibition():
    data = load()
    show_current()
    try:
        idx = int(input("\nНомер выставки для удаления (0 = отмена): ")) - 1
        if idx < 0:
            return
        removed = data['exhibitions'].pop(idx)
        save(data)
        print(f"🗑️ Удалена: {removed['title']}")
    except (ValueError, IndexError):
        print("❌ Неверный номер")


def mark_past():
    """Пометить выставки как прошедшие."""
    data = load()
    current = [ex for ex in data['exhibitions'] if ex.get('status') == 'current']
    if not current:
        print("Нет текущих выставок")
        return
    
    print("\nТекущие выставки:")
    for i, ex in enumerate(current, 1):
        print(f"  {i}. {ex['title']}")
    
    try:
        idx = int(input("Номер для пометки как 'прошедшая' (0 = отмена): ")) - 1
        if idx < 0:
            return
        current[idx]['status'] = 'past'
        save(data)
        print(f"✅ Помечена как прошедшая: {current[idx]['title']}")
    except (ValueError, IndexError):
        print("❌ Неверный номер")


def main():
    print("🎨 Редактор выставок Эрмитажа")
    print("=" * 40)

    while True:
        print("\nЧто сделать?")
        print("  1. Показать все выставки")
        print("  2. Добавить выставку")
        print("  3. Удалить выставку")
        print("  4. Пометить как прошедшую")
        print("  0. Выход")

        choice = input("\nВыбор: ").strip()

        if choice == '1':
            show_current()
        elif choice == '2':
            add_exhibition()
        elif choice == '3':
            remove_exhibition()
        elif choice == '4':
            mark_past()
        elif choice == '0':
            print("\nГотово! Теперь выполните:")
            print("  git add exhibitions.json")
            print("  git commit -m 'update exhibitions'")
            print("  git push")
            break
        else:
            print("Неверный выбор")


if __name__ == '__main__':
    main()
