FROM python:3.11-slim

WORKDIR /app

COPY rpg-api/requirements.txt .
RUN pip install -r requirements.txt

COPY rpg-api/app.py .
COPY rpg-source/monsters.csv .

EXPOSE 5000

CMD ["python", "app.py"]