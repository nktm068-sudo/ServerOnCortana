# 1. Используем легкий официальный образ Python
FROM python:3.10-slim

# 2. Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 3. Создаем рабочую папку
WORKDIR /app

# 4. Копируем файл зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Копируем сам серверный код
# 5. Копируем сам серверный код
COPY main.py .

# 6. Запуск сервера Nova
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
