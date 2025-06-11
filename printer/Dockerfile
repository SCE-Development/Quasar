# Base image from https://github.com/DrPsychick/docker-cups-airprint
# Docker images are here https://hub.docker.com/r/drpsychick/airprint-bridge/tags
FROM drpsychick/airprint-bridge:latest

WORKDIR /app

RUN apt-get update

RUN apt install -y python3 python3-pip python3-venv jq ssh

# Create a virtual environment
RUN python3 -m venv /opt/venv

# Set the virtual environment as the default Python environment
ENV PATH="/opt/venv/bin:$PATH"

COPY ./printer/requirements.txt  /app/printer/requirements.txt
COPY ../collector/requirements.txt /app/collector/requirements.txt

RUN /opt/venv/bin/pip install -r /app/printer/requirements.txt
RUN /opt/venv/bin/pip install -r /app/collector/requirements.txt

COPY ./config/config.json /app/config/config.json

COPY ./printer/what.sh /app/printer/what.sh

COPY ./printer/*.py /app/printer/
COPY ./collector/server.py /app/collector/server.py

EXPOSE 5000 9000

# The below command runs the bash script that sets up the connection to the
# printers and runs PrintHandler.js
ENTRYPOINT [ "sh", "-c", "./printer/what.sh & python3 /app/collector/server.py \"$@\"" ]
CMD ["--config-file-path", "/app/config/config.json"]

