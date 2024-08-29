#!/bin/bash

#cd src
#cd app

.venv/bin/alembic upgrade head
.venv/bin/gunicorn src.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000

## скрипт для запуска миграции и сервера