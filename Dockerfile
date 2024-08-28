FROM python:3.11-slim

RUN mkdir /app && mkdir /app/serts && mkdir /app/src && mkdir /app/docker

WORKDIR /app
RUN pip install --upgrade pip
COPY poetry.lock pyproject.toml ./

RUN python -m pip install --no-cache-dir poetry==1.8.3 \
    && poetry config virtualenvs.in-project true \
    && poetry install --without dev --no-interaction --no-ansi

COPY serts /app/serts
COPY src /app/src
COPY docker /app/docker

RUN chmod a+x docker/*.sh     # разрешение на запуск скриптов из каталога docker

#WORKDIR src

#CMD gunicorn src.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000

CMD /app/.venv/bin/gunicorn src.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000

