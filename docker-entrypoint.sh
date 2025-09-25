#!/bin/bash

# Entrypoint script for backend container
# This script runs database migrations before starting the application

set -e

echo "Starting backend container..."

# Wait for database to be ready
echo "Waiting for database to be ready..."
while ! python -c "
import asyncio
import asyncpg
import os
import sys

async def check_db():
    try:
        conn = await asyncpg.connect(
            host='postgres',
            port=5432,
            user='postgres', 
            password='password',
            database='review_db'
        )
        await conn.close()
        print('Database is ready!')
        return True
    except Exception as e:
        print(f'Database not ready: {e}')
        return False

if not asyncio.run(check_db()):
    sys.exit(1)
"; do
  echo "Database not ready, waiting..."
  sleep 2
done

# Check if alembic is available and run migrations
echo "Running database migrations..."
echo "Current directory: $(pwd)"
echo "Contents of current directory:"
ls -la
echo "Checking if alembic.ini exists:"
ls -la alembic.ini || echo "alembic.ini not found"
echo "Checking migrations directory:"
ls -la app/infra/db/migrations/versions/ || echo "migrations directory not found"

# Set PYTHONPATH to include current directory
export PYTHONPATH=/app:$PYTHONPATH

if [ -f "alembic.ini" ]; then
    echo "Running alembic upgrade head..."
    python -m alembic upgrade head 2>&1 || echo "Alembic failed with exit code $?"
    
    echo "Checking alembic current state..."
    python -m alembic current 2>&1 || echo "Alembic current failed"
    
    echo "Migrations completed successfully"
else
    echo "Warning: alembic.ini not found, skipping migrations"
fi

# Start the application
echo "Starting FastAPI application..."
exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
