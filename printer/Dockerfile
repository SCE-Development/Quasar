# Base image from https://github.com/DrPsychick/docker-cups-airprint
FROM drpsychick/airprint-bridge:latest

WORKDIR /app

# Because the base image we are using doesn't have node or npm installed, we
# have to do so before running the printing container. The below steps set up
# node and npm.
RUN apt-get update
ENV NODE_VERSION=16.13.0
RUN apt install -y curl 
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
ENV NVM_DIR=/root/.nvm
RUN . "$NVM_DIR/nvm.sh" && nvm install ${NODE_VERSION}
RUN . "$NVM_DIR/nvm.sh" && nvm use v${NODE_VERSION}
RUN . "$NVM_DIR/nvm.sh" && nvm alias default v${NODE_VERSION}
ENV PATH="/root/.nvm/versions/node/v${NODE_VERSION}/bin/:${PATH}"
# Node and NPM are now set up. The next steps copy the required files into
# the container. By copying the files over later, the setup steps for npm
# and node remain cached to speed up subsequent rebuilds.

COPY ./package.json .

COPY ./package-lock.json .

RUN npm install

COPY ./config/config.json /app/config/config.json

COPY ./printer /app/printer

COPY /util /app/util

# The below command runs the bash script that sets up the connection to the
# printers and runs PrintHandler.js
ENTRYPOINT [ "./printer/what.sh" ]
