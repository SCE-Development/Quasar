const {exec} = require('child_process');
const { stdout, stderr } = require('process');
const logger = require('../../util/logger.js');


function pingIP(ipAddress) {
    return new Promise((resolve) => {
        try{
            exec(`ping -c 5 ${ipAddress}`, (error, stdout, stderr) => {
                if(error){
                    logger.error(`error: ${error.message}`);
                    resolve(false);
                }
                if(stderr){
                    logger.error(`error: ${error.message}`);
                    resolve(false);
                } 
                else if (stdout){
                    const output = stdout;
                    const outArray = output.split('/');
                    const parse = outArray[4];
                    const time = parse.split(" ");
                    console.log('Ping latency: ', Math.round(time[0]));
                    
                    
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


