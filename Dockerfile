FROM python:3.10.2-slim-buster

WORKDIR /app

COPY requirements.txt /app

RUN pip install -r /app/requirements.txt

EXPOSE 5000

ENTRYPOINT [ "python", "server.py" ]
