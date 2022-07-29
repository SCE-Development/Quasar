#!/bin/sh
# in https://stackoverflow.com/a/41518225 we trust


# use jq to parse various config.json variables
export FETCH_INTERVAL_SECONDS=$(jq -r '.PRINTING.FETCH_INTERVAL_SECONDS' config/config.json)
export INFLUX_URL=$(jq -r '.PRINTING.INFLUX_URL' config/config.json)
export NAMES=`cat "config/config.json" |awk '/"NAME":./{print $2}'|sed -e ':a' -e 'N' -e '$!ba' -e 's/\n/ /g' -e ' '|sed -e 's/ //g' -e 's/.$//' `
export IPS=`cat "config/config.json" |awk '/            "IP":/{print $2}'|sed -e ':a' -e 'N' -e '$!ba' -e 's/\n/ /g' -e ' '|sed -e 's/ //g' -e 's/.$//' `

# export LEFT_PRINTER_IP=$(jq -r '.PRINTING.LEFT.IP' config/config.json)
# export PRINTER_LEFT_NAME=$(jq -r '.PRINTING.LEFT.NAME' config/config.json) 
# export RIGHT_PRINTER_IP=$(jq -r '.PRINTING.RIGHT.IP' config/config.json)
# export PRINTER_RIGHT_NAME=$(jq -r '.PRINTING.RIGHT.NAME' config/config.json) 


nodemon --legacy-watch ./printer/scraper/main.js --printer_ips $IPS\
    --fetch_interval_seconds $FETCH_INTERVAL_SECONDS\
    --printer_names $NAMES\
    --influx_url $INFLUX_URL
