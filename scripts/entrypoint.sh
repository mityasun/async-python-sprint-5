#!/bin/sh

# wait for db
sleep 3

alembic upgrade head
echo "Applying migrations..."
gunicorn --chdir src -k uvicorn.workers.UvicornWorker -w 1 -b 0.0.0.0:8000 src.main:app
echo "Start service..."