# Base image from https://github.com/DrPsychick/docker-cups-airprint
# Docker images are here https://hub.docker.com/r/drpsychick/airprint-bridge/tags
FROM drpsychick/airprint-bridge:latest

WORKDIR /app

RUN apt-get update

RUN apt-get install -y software-properties-common \
 && add-apt-repository ppa:deadsnakes/ppa \
 && apt-get update \
 && apt-get install -y python3.11 python3.11-venv python3.11-dev jq ssh

# Create the virtual environment with Python 3.11
RUN python3.11 -m venv /opt/venv

# Set the virtual environment as the default Python environment
ENV PATH="/opt/venv/bin:$PATH"

COPY ./printer/requirements.txt  /app/printer/requirements.txt

RUN /opt/venv/bin/pip install -r /app/printer/requirements.txt

COPY ./config/config.json /app/config/config.json

COPY ./printer/what.sh /app/printer/what.sh

COPY ./printer/*.py /app/printer/

EXPOSE 9000

# The below command runs the bash script that sets up the connection to the
# printers and runs PrintHandler.js
ENTRYPOINT [ "./printer/what.sh" ]

