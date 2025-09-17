#!/bin/sh

# MAKE SURE THIS FILE IS USING LF FOR ITS EOL SEQUENCE!!!!!!!!!!!
# OTHERWISE DOCKER WILL COMPLAIN THAT THIS FILE DOESNT EXIST!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

/root/start-cups.sh > /dev/null 2>&1 & 

sleep 10

lpadmin -p HP_LaserJet_p2015dn_Right -E -v file:///dev/null

python3 /app/printer/server.py $@