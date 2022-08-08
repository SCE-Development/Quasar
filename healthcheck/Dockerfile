FROM python:3.9.6-slim-buster

WORKDIR /app

RUN pip install flask requests
RUN apt-get update
RUN apt-get install -y jq ssh

COPY ./healthcheck/* /app/tunnel/
COPY ./config/config.json /app/config/

EXPOSE 9000
ENTRYPOINT ["/app/tunnel/tun.sh"]
