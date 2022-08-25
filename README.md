# Quasar
How paper is printed at SCE.

## Running the project
- [ ] Clone this project with
```
git clone https://github.com/SCE-Development/Quasar.git
```
- [ ] Make a copy of `config/config.example.json` to `config/config.json`
- [ ] fill out `config/config.json` with the appropriate values:
```json
{
    "AWS": {
        "ACCESS_ID": "get this from an officer",
        "SECRET_KEY": "get this from an officer",
        "ACCOUNT_ID": "get this from an officer",
        "DEFAULT_REGION": "us-west-2"
    },
    "HEALTH_CHECK": {
        "CORE_V4_IP": "this is an ip address, i.e. 127.0.0.1"
    },
    "PRINTING": {
        "QUEUE_NAME": "name from aws, e.g. my-printing-queue",
        "BUCKET_NAME": "name from aws, e.g. my-printing-bucket",
        "FETCH_INTERVAL_SECONDS": "interval sections for printing scraper",
        "INFLUX_URL": "influx url for monitoring to write to",
        "LEFT": {
            "ENABLED": true,
            "NAME": "name of left printer in sce",
            "IP": "ip address of the left printer in sce",
            "LPD_URL": "lpd://<ip address of left printer>"
        },
        "RIGHT": {
            "ENABLED": true,
            "NAME": "name of right printer in sce",
            "IP": "ip address of the right printer in sce",
            "LPD_URL": "lpd://<ip address of right printer>"
        }
    }
}
```
**Note:** Ensure on AWS you are using resources from the Oregon (`us-west-2`)
 region.
- [ ] Run the project with `docker-compose up`. The containers will run and accept messages from SQS.

## Generating SSH Keys for tunnel
**Note:** This is for deploying production Quasar only!
- Follow this
 [guide](https://www.digitalocean.com/community/tutorials/how-to-set-up-ssh-keys-2)
 to generate ssh keys on your machine
- Ensure the keys were outputted to files containing `id_ed25519`
- `docker-compose up`, the generated keys will be mounted in the health check container
