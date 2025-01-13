FROM python:3.12-slim

WORKDIR /app/

ENV INSTALL_DEV=true
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

ENV POETRY_VIRTUALENVS_CREATE=false
ENV POETRY_VIRTUALENVS_IN_PROJECT=false
ENV POETRY_PYTHON=/usr/local/bin/python
ENV TZ=Europe/Moscow
COPY . .

RUN poetry lock
RUN bash -c "if [ $INSTALL_DEV == 'true' ] ; then poetry install --no-root ; else poetry install --no-root --no-dev ; fi"

# Установка необходимых пакетов для сборки

CMD ["poetry", "run", "python", "main.py"]