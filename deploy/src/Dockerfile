FROM python:3.10-slim-buster

WORKDIR /dynamic-routing

COPY deploy/src/requirements.txt requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY src src

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]