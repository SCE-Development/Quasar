
#https://github.com/DrPsychick/docker-cups-airprint
FROM drpsychick/airprint-bridge:latest

##################################
WORKDIR /app

RUN apt-get update
ENV NODE_VERSION=16.13.0
RUN apt install -y curl
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
ENV NVM_DIR=/root/.nvm
RUN . "$NVM_DIR/nvm.sh" && nvm install ${NODE_VERSION}
RUN . "$NVM_DIR/nvm.sh" && nvm use v${NODE_VERSION}
RUN . "$NVM_DIR/nvm.sh" && nvm alias default v${NODE_VERSION}
ENV PATH="/root/.nvm/versions/node/v${NODE_VERSION}/bin/:${PATH}"
RUN node --version
RUN npm --version

COPY ./package.json .

COPY ./package-lock.json .

RUN npm install

COPY ./printer /app/printer

COPY ./config/config.json /app/config/config.json
############################

COPY what.sh .

RUN chmod +x what.sh

ENTRYPOINT [ "./what.sh" ]