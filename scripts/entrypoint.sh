#!/bin/sh

set -e
DB_HOST='files_postgres'
DB_PORT=5432

if [ -n "$DB_HOST" -a -n "$DB_PORT" ]
then
    while ! nc -vz "${DB_HOST}" "${DB_PORT}"; do
        echo "Waiting for database..."
        sleep 1;
    done
fi

alembic upgrade head
echo "Applying migrations..."
gunicorn --chdir src -k uvicorn.workers.UvicornWorker -w 1 -b 0.0.0.0:8000 src.main:app
echo "Start service..."