FROM python:3:13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENV TELEGRAM_TOKEN=your_token_here

CMD ["python", "main.py"]


