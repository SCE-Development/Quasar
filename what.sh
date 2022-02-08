#!/bin/sh
# in https://stackoverflow.com/a/41518225 we trust

# spawn new process for cups server

create_and_enable_printer() {
    lpadmin -p $1 -v $2
    lpadmin -d $1 -P /etc/cups/ppd/HP-LaserJet-p2015dn.ppd
    cupsenable $1 && cupsaccept $1
}


/root/start-cups.sh > /dev/null 2>&1 & 

sleep 10

create_and_enable_printer $LEFT_PRINTER_NAME $LEFT_PRINTER_IP
create_and_enable_printer $RIGHT_PRINTER_NAME $RIGHT_PRINTER_IP

node printer/PrintHandler.js
