#!/bin/sh

# get Core-v4 ip from config.json
CORE_V4_IP=$(cat /app/config/config.json | jq -r ".HEALTH_CHECK.CORE_V4_IP") 

# known_hosts remembers servers we've ssh'd into in the past.
# ssh can use this file to verify the legitimacy of CORE_V4_IP.
# So, we know for sure that we're setting up a connection to Core-v4
DOCKER_CONTAINER_KNOWN_HOSTS=/app/known_hosts

# This is Quasar's private ssh key. It's needed in order to connect
# to Core-v4. Without this, ssh cannot decrypt data coming from
# Core-v4
DOCKER_CONTAINER_SSH_KEYS=/app/ssh_key

# This is the port on Core-v4 that will be forwarded into the conn
# container (try curl localhost:CORE_V4_PORT in Core-v4). Software responisble
# to check health checks, on Core-v4 will communicate with the container
# through Core-v4's localhost:CORE_V4_PORT.
CORE_V4_PORT=14000 

# This port is where Quasar should report health checks. Through this port,
# Quasar has a connection to Core-v4. Typically, Quasar will only be sending data
# out to Core-v4. 
QUASAR_PORT=9000

# intermediate variable to feed ssh command. It will look like sce@XXX.XXX.XXX.XXX
CORE_V4_HOST=sce@${CORE_V4_IP}

# Start the tunnel!
open_ssh_tunnel () {
    # (more info about the switches can be found in "man ssh")
    # -o is for option to give known_hosts
    # -i is for giving Quasar's private key
    # -f -N makes ssh run in the background. We don't need a shell because
    #   we are just creating a tunnel.
    # -R is to port forward. This is actually what creates the tunnel! 
    #   This forwards packets created in Core-v4 and sent into its 
    #   localhost:CORE_V4_PORT to Quasar's localhost:QUASAR_PORT and vise-versa.
    #   Consequently, this creates the tunnel from Core-v4:CORE_V4_PORT to
    #   Quasar:QUASAR_PORT
    # Lastly, CORE_V4_HOST is given to signify the user and ip of Core-v4.

    ssh -v \
    -o UserKnownHostsFile=${DOCKER_CONTAINER_KNOWN_HOSTS} \
    -o StrictHostKeyChecking=no \
    -i ${DOCKER_CONTAINER_SSH_KEYS} \
    -f -g -N -R 0.0.0.0:${CORE_V4_PORT}:localhost:${QUASAR_PORT} ${CORE_V4_HOST}
}

# Change file permissions of the private key.
# 600 means only the owner should be able to read/write the file.
# If the permissions aren't tight, ssh complains and doesn't connect. 
chmod 600 ${DOCKER_CONTAINER_SSH_KEYS}


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

# if the first argument passed to the script, is --tunnel-only,
# we just open the ssh tunnel. i.e.
#
# $ ./what.sh --tunnel-only
# 
# to open the tunnel and start the server:
# $ ./tun.sh <args we want to send to the python server>
#
# the above args are passed to the python script with the $@ variable,
# for more info on $@, see https://stackoverflow.com/a/3811369
if [ "$1" = "--tunnel-only" ]
then
    open_ssh_tunnel
else
    # The below command starts CUPS in the background. Our base image for the
    # printing container comes with /root/start-cups.sh. Because the print
    # container is built from said image, the script comes with the build steps. 
    # To see the actual script, check out the below link:
    # https://github.com/DrPsychick/docker-cups-airprint/blob/d4c701b5a2897897413b22bd705c74159a579acc/start-cups.sh
    /root/start-cups.sh > /dev/null 2>&1 & 

    # CUPS takes a bit to start running, so before we add our two SCE printers the
    # script hangs out for 10 seconds.
    sleep 10

    # Call the above function for the left and right printers, both values
    # defined in an .env file. See this repo's README.md for more info.
    if [ $(cat config/config.json | jq ".PRINTING.LEFT.ENABLED") = "true"  ]; then
        export LEFT_PRINTER_NAME=$(jq -r '.PRINTING.LEFT.NAME' config/config.json)
        export LEFT_PRINTER_LPD_URL=$(jq -r '.PRINTING.LEFT.LPD_URL' config/config.json)                         
        create_and_enable_printer $LEFT_PRINTER_NAME $LEFT_PRINTER_LPD_URL
    fi

    if [ $(cat config/config.json | jq ".PRINTING.RIGHT.ENABLED") = "true"  ]; then
        export RIGHT_PRINTER_NAME=$(jq -r '.PRINTING.RIGHT.NAME' config/config.json)
        export RIGHT_PRINTER_LPD_URL=$(jq -r '.PRINTING.RIGHT.LPD_URL' config/config.json)                       
        create_and_enable_printer $RIGHT_PRINTER_NAME $RIGHT_PRINTER_LPD_URL
    fi
    open_ssh_tunnel
    python3 /app/printer/server.py $@
fi

