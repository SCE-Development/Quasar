# Quasar
How paper is printed at SCE.

## Running the project (development)
Clone the SCE dev tool and follow the guide for setup: https://github.com/SCE-Development/SCE-CLI#setup

```
sce clone q

cd Clark

sce link q
```
- [ ] Make a copy of `config/config.example.json` to `config/config.json`
- [ ] fill out `config/config.json` with the appropriate values:
```json
{
    "HEALTH_CHECK": {
        "CORE_V4_IP": "this is an ip address, i.e. 127.0.0.1"
    },
    "PRINTING": {
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
- [ ] Run the project with `sce run q`. The server will run and accept requests on http://localhost:14000.

## Running the project (production)
### Generating SSH Keys for tunnel
**Note:** This is for deploying production Quasar only!
- Follow this
 [guide](https://www.digitalocean.com/community/tutorials/how-to-set-up-ssh-keys-2)
 to generate ssh keys on your machine
- Ensure the keys were outputted to files containing `id_ed25519`
- `docker-compose up`, the generated keys will be mounted in the health check container
### Modifying the config.json
- make sure to set the `ENABLED` field to true for the printer you wish to print at
- ensure the `IP` and `LPD_URL` field are using the same IP address of the corresponding printer
- the `NAME` field can be whatever you want, i.e. `right-printer`. It's for the `lp` command to use in sending the print request

