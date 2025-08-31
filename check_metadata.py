#!/usr/bin/env python3
"""
Скрипт для проверки регистрации моделей в metadata.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("1. Состояние metadata ДО импорта моделей:")
from app.infra.db.base import Base
print(f"   Таблицы в metadata: {list(Base.metadata.tables.keys())}")

print("\n2. Импортируем модели...")
from app.infra.db.models import Task, UserSession

print("3. Состояние metadata ПОСЛЕ импорта моделей:")
print(f"   Таблицы в metadata: {list(Base.metadata.tables.keys())}")

print("\n4. Детали таблиц:")
for table_name, table in Base.metadata.tables.items():
    print(f"   - {table_name}: {len(table.columns)} колонок, {len(table.indexes)} индексов")
