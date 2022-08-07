const { logger } = require('../util/logger');
const exec = require('exec');
const client = require('prom-client');
const express = require('express');
const app = express();
let register = new client.Registry();

canPing = new client.Gauge({
    name: `canPing`,
    help: `canPing_help`,
  });

  
client.collectDefaultMetrics({ register });
register.setDefaultLabels ({
    app: 'ping-temp'
});
register.registerMetric(canPing)

app.get('/metrics', async (request, response) => {
    response.setHeader('Content-Type', register.contentType);
    response.end(await register.metrics());
});
  
app.listen(5000, () =>{
    console.log('Started server on port 5000');
});


function pingIP(ipAddress) {
    return new Promise((resolve) => {
        try{
            exec(`ping -c 5 ${ipAddress}`, (error, stdout, stderr) => {
                if(error){
                    logger.error(`error: ${error.message}`);
                    canPing.set(0)
                    resolve(false);
                }
                if(stderr){
                    logger.error(`error: ${error.message}`);
                    canPing.set(0)
                    resolve(false);
                } 
                else if (stdout){
                    canPing.set(1)
                    resolve(true);
                }
            });
        } catch(error){
            logger.error('function had an error: ', error);
            resolve(false);
        }
    });
    
}

const ipAddress = '8.8.8.8';

for(let i = 0; i < 10; i++){
    pingIP(ipAddress);
}