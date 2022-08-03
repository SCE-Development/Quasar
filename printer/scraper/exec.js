const {exec} = require('child_process');
const { stdout, stderr } = require('process');
const logger = require('../../util/logger.js');


exec('ping -c 5 8.8.8.8', (error, stdout, stderr) => {
    if(error){
        logger.error(`error: ${error.message}`);
        return false;
    }
    if(stdout){
        logger.info('succesfully pinged')
        return true;
    }
    if(stderr)
    {
        logger.error(`error: ${error.message}`);
        return false;
    }

});