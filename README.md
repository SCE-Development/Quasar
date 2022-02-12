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
    "LED_URL": "http://<led ip address>/"
}
```
**Note:** Ensure on AWS you are using resources from the Oregon (`us-west-2`)
 region.

- [ ] Create a `.env` file in the `Quasar/` directory with contents
```sh
LEFT_PRINTER_NAME=HP-LaserJet-p2015dn-left
LEFT_PRINTER_IP=lpd://<ip>?format=l

RIGHT_PRINTER_NAME=HP-LaserJet-p2015dn-right
RIGHT_PRINTER_IP=lpd://<ip>?format=l

AWS_ACCESS_KEY_ID=get this from aws
AWS_SECRET_ACCESS_KEY=get this from aws
AWS_DEFAULT_REGION=us-west-2
```
**Note:** Do not wrap the values of each variables in quotes. Paste the raw values only.
- [ ] Run the project with `docker-compose up`. The containers will run and accept messages from SQS.

