#!/bin/sh

/root/start-cups.sh > /dev/null 2>&1 & 

sleep 10

lpadmin -p dev_printer -E -v file:///dev/null

python3 /app/printer/server.py $@
