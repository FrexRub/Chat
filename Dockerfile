FROM python:3.11-slim

RUN mkdir /app && mkdir /app/serts && mkdir /app/src && mkdir /app/docker && mkdir /app/alembic

WORKDIR /app
RUN pip install --upgrade pip
COPY poetry.lock pyproject.toml ./

RUN python -m pip install --no-cache-dir poetry==1.8.3 \
    && poetry config virtualenvs.in-project true \
    && poetry install --without dev --no-interaction --no-ansi

COPY alembic.ini /app
COPY serts /app/serts
COPY docker /app/docker
COPY alembic /app/alembic
COPY src /app/src


RUN chmod a+x docker/*.sh     # разрешение на запуск скриптов из каталога docker

#CMD /app/.venv/bin/gunicorn src.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000

