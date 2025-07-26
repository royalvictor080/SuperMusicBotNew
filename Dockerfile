FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN apt-get update && apt-get install -y ffmpeg git && pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python3", "main.py"]
