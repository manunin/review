#!/bin/bash

# Проверка задач в PostgreSQL
docker exec review-postgres-1 psql -U postgres -d review_db -c "SELECT task_id, type, status, user_id, created_at, updated_at FROM tasks ORDER BY created_at DESC LIMIT 5;"
