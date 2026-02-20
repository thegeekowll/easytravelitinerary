#!/bin/bash
set -e

echo "=== Waiting for database to be ready ==="
until pg_isready -h "${POSTGRES_SERVER:-postgres}" -p "${POSTGRES_PORT:-5432}" -U "${POSTGRES_USER:-postgres}" > /dev/null 2>&1; do
    echo "Database is not ready yet... waiting"
    sleep 2
done
echo "Database is ready!"

echo "=== Running database migrations ==="
cd /app
alembic upgrade head || {
    echo "Migration failed, but continuing startup..."
    echo "The database tables might already exist or need manual intervention."
}

echo "=== Starting application ==="
exec "$@"
