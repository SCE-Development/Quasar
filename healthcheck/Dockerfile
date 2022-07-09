FROM python:3.9.6-slim-buster

WORKDIR /app

RUN pip install flask
RUN apt-get update
RUN apt-get install -y jq ssh

COPY ./healtcheck/* /app/healtcheck/
COPY ./config/config.json /app/config/

ENTRYPOINT ["/app/healtcheck/tun.sh"]
