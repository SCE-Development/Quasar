# Base image from https://github.com/DrPsychick/docker-cups-airprint
# Docker images are here https://hub.docker.com/r/drpsychick/airprint-bridge/tags
FROM drpsychick/airprint-bridge:jammy

WORKDIR /app

RUN apt-get update

RUN apt install -y python3 python3-pip python3-venv jq ssh ghostscript

# Create the virtual environment with Python
RUN python3 -m venv /opt/venv

# Set the virtual environment as the default Python environment
ENV PATH="/opt/venv/bin:$PATH"

COPY ./printer/requirements.txt  /app/printer/requirements.txt

RUN /opt/venv/bin/pip install -r /app/printer/requirements.txt

EXPOSE 9000

# The below command runs the bash script that sets up the connection to the
# printers and runs PrintHandler.js
ENTRYPOINT [ "./printer/what.sh" ]

