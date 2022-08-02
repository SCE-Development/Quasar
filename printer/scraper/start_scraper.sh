#!/bin/sh
# in https://stackoverflow.com/a/41518225 we trust

export FETCH_INTERVAL_SECONDS=$(jq -r '.PRINTING.FETCH_INTERVAL_SECONDS' config/config.json)
export INFLUX_URL=$(jq -r '.PRINTING.INFLUX_URL' config/config.json)
export NAMES=`cat "config/config.json" |awk '/"NAME":./{print $2}'|sed -e ':a' -e 'N' -e '$!ba' -e 's/\n/ /g' -e ' '|sed -e 's/ //g' -e 's/.$//' `
export IPS=`cat "config/config.json" |awk '/            "IP":/{print $2}'|sed -e ':a' -e 'N' -e '$!ba' -e 's/\n/ /g' -e ' '|sed -e 's/ //g' -e 's/.$//' `

nodemon --legacy-watch ./printer/scraper/main.js --printer_ips $IPS\
    --fetch_interval_seconds $FETCH_INTERVAL_SECONDS\
    --printer_names $NAMES\
    --influx_url $INFLUX_URL
