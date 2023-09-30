# Base image from https://github.com/DrPsychick/docker-cups-airprint
FROM drpsychick/airprint-bridge:latest

WORKDIR /app

RUN apt-get update

RUN apt install -y python3 python3-pip jq ssh

COPY ./printer/requirements.txt /app/printer/requirements.txt

RUN python3 -m pip install -r /app/printer/requirements.txt

COPY ./config/config.json /app/config/config.json

COPY ./printer/what.sh /app/printer/what.sh

COPY ./printer/*.py /app/printer/

EXPOSE 9000

# The below command runs the bash script that sets up the connection to the
# printers and runs PrintHandler.js
ENTRYPOINT [ "./printer/what.sh" ]
