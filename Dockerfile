FROM python:3:13-slim

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENV TELEGRAM_TOKEN=7637793439:AAGyrqw8krgxQyiEkvQ7-w20y5FBfYwkLNQ

CMD ["python", "main.py"]


