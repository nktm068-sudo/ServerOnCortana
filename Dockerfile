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
COPY app.py .

# Строку EXPOSE можно убрать, так как Render сам управляет портами изнутри

# 6. Запуск: используем bash-оболочку, чтобы uvicorn прочитал переменную $PORT, 
# а если её нет (например, локально), то включится порт 8000 по умолчанию
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}"]
