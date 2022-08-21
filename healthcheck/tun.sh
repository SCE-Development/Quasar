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
    -i ${DOCKER_CONTAINER_SSH_KEYS} \
    -f -g -N -R 0.0.0.0:${CORE_V4_PORT}:localhost:${QUASAR_PORT} ${CORE_V4_HOST}
}


# Change file permissions of the private key.
# 600 means only the owner should be able to read/write the file.
# If the permissions aren't tight, ssh complains and doesn't connect. 
chmod 600 ${DOCKER_CONTAINER_SSH_KEYS}

# call ssh tunnel function
open_ssh_tunnel

# app.py reports health checks to localhost:QUASAR_PORT.
# Core-v4 gets health check data from this.
python /app/tunnel/app.py ${QUASAR_PORT}

