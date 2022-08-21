# Quasar
Code for all of the SCE peripherals (printer + LED sign).

## Running the project
- [ ] Clone this project with
```
git clone https://github.com/SCE-Development/Quasar.git
```
- [ ] Make a copy of `config/config.example.json` to `config/config.json`
- [ ] fill out `config/config.json` with the appropriate values:
```json
{
    "ACCESS_ID": "get this from an officer",
    "SECRET_KEY": "get this from an officer",
    "ACCOUNT_ID": "get this from an officer",
    "LED_QUEUE_NAME": "name from aws, e.g. my-led-queue",
    "PRINTING_QUEUE_NAME": "name from aws, e.g. my-printing-queue",
    "PRINTING_BUCKET_NAME": "name from aws, e.g. my-printing-bucket",
    "LED_URL": "http://<led ip address>/",
    "PRINTER_LEFT_IP": "ip address of the left printer in sce",
    "PRINTER_RIGHT_IP": "ip address of the right printer in sce",
    "CORE_V4_IP" : "ip address of the core-v4 computer in sce",
    "PRINTER_LEFT_NAME": "name of left printer in sce",
    "PRINTER_RIGHT_NAME": "name of right printer in sce",
    "AWS_DEFAULT_REGION": "us-west-2"
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
