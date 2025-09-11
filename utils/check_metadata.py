#!/usr/bin/env python3
"""
Скрипт для проверки регистрации моделей в SQLAlchemy metadata.

Показывает, как модели автоматически регистрируются в Base.metadata
при импорте через механизм DeclarativeBase.

Использование:
    python utils/check_metadata.py
"""

import sys
import os

# Добавляем корень проекта в PYTHONPATH
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

print("🔍 Проверка регистрации моделей в SQLAlchemy metadata")
print("=" * 60)

print("\n1. Состояние metadata ДО импорта моделей:")
from app.infra.db.base import Base
print(f"   📋 Таблицы в metadata: {list(Base.metadata.tables.keys())}")
print(f"   📊 Количество таблиц: {len(Base.metadata.tables)}")

print("\n2. ⚡ Импортируем модели...")
from app.tasks.models import Task
from app.infra.db.sessions import UserSession

print("3. Состояние metadata ПОСЛЕ импорта моделей:")
print(f"   📋 Таблицы в metadata: {list(Base.metadata.tables.keys())}")
print(f"   📊 Количество таблиц: {len(Base.metadata.tables)}")

print("\n4. 📝 Детали таблиц:")
for table_name, table in Base.metadata.tables.items():
    print(f"   - 🗂️  {table_name}:")
    print(f"     • {len(table.columns)} колонок")
    print(f"     • {len(table.indexes)} индексов")
    print(f"     • {len([c for c in table.columns if c.primary_key])} первичных ключей")
    print(f"     • {len([c for c in table.columns if c.foreign_keys])} внешних ключей")

print("\n5. 📋 Колонки по таблицам:")
for table_name, table in Base.metadata.tables.items():
    print(f"\n   🗂️  {table_name}:")
    for column in table.columns:
        pk = " (PK)" if column.primary_key else ""
        fk = " (FK)" if column.foreign_keys else ""
        nullable = "NULL" if column.nullable else "NOT NULL"
        print(f"     • {column.name}: {column.type} {nullable}{pk}{fk}")

print("\n" + "=" * 60)
print("✅ Вывод: Импорт 'from app.tasks.models import Task' и 'from app.infra.db.sessions import UserSession'")
print("   автоматически регистрирует модели в Base.metadata")
