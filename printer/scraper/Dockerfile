FROM node:14.10.0-alpine
#gets the base linux image

WORKDIR /app
#all commands will run in this directory

COPY ./package.json .
#copies all the dependenices into work directory (./app) (since you set the work dir before)

RUN npm install
#installs packages

RUN apk add jq

COPY ./printer /app/printer
#copies this file to the desination

COPY ./util /app/util
#copies this file to the desination

COPY ./config /app/config

RUN  chmod +x ./printer/scraper/start_scraper.sh

ENTRYPOINT ["./printer/scraper/start_scraper.sh"]