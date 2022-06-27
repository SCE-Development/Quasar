FROM node:14.10.0-alpine 
#gets the base linux image

WORKDIR /app
#all commands will run in this directory

COPY ../package.json .
#copies all the dependenices into work directory (./app) (since you set the work dir before)

RUN npm install 
#installs packages

COPY ./printer /app
#copies this file to the desination

COPY ../../util /app
#copies this file to the desination

RUN ls

#for test case only it is 5 CHANGE THAT SOON!!
# sippin tea in yo hood wtf is up 
CMD [ "node", "./scraperPrinter/scraper.js", "--printer_ip", "192.168.1.51", "--fetch_interval_seconds", "5", "--printer_name", "right","--influx_url", "http://quasar_influx.quasar_default:8086"]
