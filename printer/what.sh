#!/bin/sh
# in https://stackoverflow.com/a/41518225 we trust

# This function sets up the left and right printer to be used
# with the Line Printer Daemon protocol. To read more about it
# check out the below link:
# https://en.wikipedia.org/wiki/Line_Printer_Daemon_protocol
create_and_enable_printer() {
    echo "Setting up $1 with ip address $2"
    lpadmin -p $1 -v $2
    lpadmin -d $1 -P /etc/cups/ppd/HP-LaserJet-p2015dn.ppd
    cupsenable $1 && cupsaccept $1
}

# The below command starts CUPS in the background. Our base image for the
# printing container comes with /root/start-cups.sh. Because the print
# container is built from said image, the script comes with the build steps. 
# To see the actual script, check out the below link:
# https://github.com/DrPsychick/docker-cups-airprint/blob/d4c701b5a2897897413b22bd705c74159a579acc/start-cups.sh
/root/start-cups.sh > /dev/null 2>&1 & 

# CUPS takes a bit to start running, so before we add our two SCE printers the
# script hangs out for 10 seconds.
sleep 10

# we set these environment variables as the AWS S3 node library will
# throw errors otherwise.
export AWS_ACCESS_KEY_ID=$(jq -r '.AWS.ACCESS_ID' config/config.json)
export AWS_SECRET_ACCESS_KEY=$(jq -r '.AWS.SECRET_KEY' config/config.json)
export AWS_DEFAULT_REGION=$(jq -r '.AWS.DEFAULT_REGION' config/config.json)

# Call the above function for the left and right printers, both values
# defined in an .env file. See this repo's README.md for more info.
if [ $(cat config/config.json | jq ".PRINTING.LEFT.ENABLED") = "true"  ]; then
    export LEFT_PRINTER_NAME=$(jq -r '.PRINTING.LEFT.NAME' config/config.json)
    export LEFT_PRINTER_LPD_URL=$(jq -r '.PRINTING.LEFT.LPD_URL' config/config.json)                                                                                ─╯
    create_and_enable_printer $LEFT_PRINTER_NAME $LEFT_PRINTER_LPD_URL
fi

if [ $(cat config/config.json | jq ".PRINTING.RIGHT.ENABLED") = "true"  ]; then
    export RIGHT_PRINTER_NAME=$(jq -r '.PRINTING.RIGHT.NAME' config/config.json)
    export RIGHT_PRINTER_LPD_URL=$(jq -r '.PRINTING.RIGHT.LPD_URL' config/config.json)                                                                             ─╯
    create_and_enable_printer $RIGHT_PRINTER_NAME $RIGHT_PRINTER_LPD_URL
fi

echo Starting print server...

# Run the actual code to read from SQS/S3 and send files to the printers.
node printer/PrintHandler.js
