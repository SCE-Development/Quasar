FROM node:14.10.0-alpine
#gets the base linux image

#all commands will run in this directory
WORKDIR /app

#copies all the dependenices into work directory (./app) (since you set the work dir before)
COPY ./package.json .

#installs packages
RUN npm install
RUN npm i -g nodemon 

RUN apk add jq

#copies this file to the desination
COPY ./printer /app/printer

#copies this file to the desination
COPY ./util /app/util

COPY ./config /app/config

RUN  chmod +x ./printer/scraper/start_scraper.sh

ENTRYPOINT ["./printer/scraper/start_scraper.sh"]