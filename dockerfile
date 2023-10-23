FROM python:latest

WORKDIR /app

COPY app.py ./

CMD ["python", "app.py"]