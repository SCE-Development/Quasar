FROM python:3.9.6-slim-buster

WORKDIR /app

RUN pip install flask
RUN apt-get update
RUN apt-get install -y jq ssh

COPY ./tunnel/* /app/tunnel/
COPY ./config/config.json /app/config/

ENTRYPOINT ["/app/tunnel/tun.sh"]
