FROM node:14.10.0-alpine
#gets the base linux image

#all commands will run in this directory
WORKDIR /app

#copies all the dependenices into work directory (./app) (since you set the work dir before)
COPY ./package.json .

#installs packages
RUN npm install
RUN npm i -g nodemon 

#copies this file to the desination
COPY ./printer /app/printer

#copies this file to the desination
COPY ./util /app/util

COPY ./config /app/config

CMD ["nodemon","--legacy-watch", "./printer/scraper/ipAddress.js"]
