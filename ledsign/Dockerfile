FROM node:8.10.0-alpine 
#gets the base linux image

WORKDIR /app
#all commands will run in this directory

COPY ./package.json .
#copies all the dependenices into work directory (./app) (since you set the work dir before)

RUN npm install 
#installs packages

COPY ./ledsign /app/ledsign
#copies this file to the desination

COPY ./config/config.json /app/config/config.json

CMD [ "node", "./ledsign/LEDSignHandler.js" ]
