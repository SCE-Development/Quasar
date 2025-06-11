FROM python:3.10.2-slim-buster

WORKDIR /app

COPY ./collector/requirements.txt /app

RUN pip install -r /app/requirements.txt

COPY ./collector/server.py /app

EXPOSE 5000

ENTRYPOINT [ "python", "server.py"]

CMD [ "--config-file-path", "/tmp/config.json"]
