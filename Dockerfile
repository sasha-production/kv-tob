FROM python:3.12.1 AS builder
# -- Медленные операции --
# Установка системных зависимостей (в т. ч. для зависимостей python)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

# Установка зависимостей python в директорию /app/wheels
RUN --mount=type=bind,source=requirements.txt,target=/app/requirements.txt \
  pip wheel --no-cache-dir --no-deps -r /app/requirements.txt --wheel-dir /app/wheels

# ---------

FROM python:3.12.1-slim

# Копирование собранных файлов python из образа builder
COPY --from=builder /app/wheels /wheels

# Установка зависимостей, которые нужны для работы приложения
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Установка зависимостей python без пересборки
RUN pip install --no-cache --no-cache-dir /wheels/*
# Not root user
RUN groupadd -r appuser && useradd -r -g appuser appuser
USER appuser
# Копирование кода приложения
COPY /bot /app/

# Установка рабочей директории
WORKDIR /app

CMD ["python3", "-m", "bot.main"]
