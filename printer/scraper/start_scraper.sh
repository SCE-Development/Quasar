#!/bin/sh

# Uses Jq to get the Fetch interval seconds and Influx URL the user assigns in the config file

export FETCH_INTERVAL_SECONDS=$(jq -r '.PRINTING.FETCH_INTERVAL_SECONDS' config/config.json)
export INFLUX_URL=$(jq -r '.PRINTING.INFLUX_URL' config/config.json)

# Dynamically gets the IP address and the Name of the printers that the user adds to config file
# Add as many printers as you want following the format
# NAMES looks like "Left, Right"
# IPS looks like "XXX.XXX.XXX.XXX, XXX.XXX.XXX.XXX"

export NAMES=`cat "config/config.json" |awk '/"NAME":./{print $2}'|sed -e ':a' -e 'N' -e '$!ba' -e 's/\n/ /g' -e ' '|sed -e 's/ //g' -e 's/.$//' `
export IPS=`cat "config/config.json" |awk '/"IP":/{print $2}'|sed -e ':a' -e 'N' -e '$!ba' -e 's/\n/ /g' -e ' '|sed -e 's/ //g' -e 's/.$//' `

nodemon --legacy-watch ./printer/scraper/main.js --printer_ips $IPS\
    --fetch_interval_seconds $FETCH_INTERVAL_SECONDS\
    --printer_names $NAMES\
    --influx_url $INFLUX_URL
