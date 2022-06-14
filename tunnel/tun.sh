#!/bin/sh

CORE_V4_IP=$(cat /app/config/config.json | jq -r ".CORE_V4_IP")
DOCKER_CONTAINER_KNOWN_HOSTS=/app/known_hosts
DOCKER_CONTAINER_SSH_KEYS=/app/test_keys
CORE_V4_PORT=14000
QUASAR_PORT=9000

CORE_V4_HOST=sce@${CORE_V4_IP}

open_ssh_tunnel () {

    ssh -v \
    -o UserKnownHostsFile=${DOCKER_CONTAINER_KNOWN_HOSTS} \
    -i ${DOCKER_CONTAINER_SSH_KEYS} \
    -f -N -R ${CORE_V4_PORT}:localhost:${QUASAR_PORT} ${CORE_V4_HOST}
}

chmod 600 ${DOCKER_CONTAINER_SSH_KEYS}

open_ssh_tunnel
python /app/tunnel/app.py ${QUASAR_PORT}

