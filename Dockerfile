# Используем образ Python
FROM python:3.13-slim

# Устанавливаем директорию в контейнере
WORKDIR /app

# Копируем файл штук
COPY requirements.txt .

#Устанавливаем все нужные штуки
RUN pip install -r requirements.txt

# Копируем все файлы в директорию контейнера
COPY . .

#Команда для запуска бота
CMD ["python", "bot.py"]
