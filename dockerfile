FROM python:3.9-slim

WORKDIR /usr/src/app

COPY . /usr/src/app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "api.api:app", "--host", "0.0.0.0", "--port", "8000"]
