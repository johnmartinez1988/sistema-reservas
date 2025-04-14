FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ./api /app/api
COPY ./tests /app/tests

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]