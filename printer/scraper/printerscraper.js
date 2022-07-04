const {PrinterScraper} = require('./printerscraper');
const logger = require('../../util/logger.js');
const rawArgs = process.argv.slice(2);
if(rawArgs.length != 8)
{
  throw new Error('Incorrect Length');
}
let printerIP = '';
let intervalSeconds = 0;
let printerName = '';
let influxUrl = '';

// perform argument checks before continuing with program
for(let i = 0; i < rawArgs.length; i += 2)
{
  switch (rawArgs[i]) {
    case '--printer_ip':
      printerIP = rawArgs[i + 1];
      break;
    case '--fetch_interval_seconds':
      intervalSeconds = rawArgs[i + 1];
      break;
    case '--printer_name':
      printerName = rawArgs[i + 1];
      break;
    case '--influx_url':
      influxUrl = rawArgs[i + 1];
      break;
    default:
      throw new Error('Check Argument: ' + rawArgs[i]);
  }
}

logger.info(`Printer IP: ${printerIP}\
 Interval: ${intervalSeconds}\
 Printer Name: ${printerName}\
 Influx URL: ${influxUrl}`);

// minimum seconds due to data receiving speed
if(intervalSeconds < 60)
{
  console.log('interval seconds has been changed to 60 seconds');
  intervalSeconds = 60;
}

let pS = new PrinterScraper(printerIP, intervalSeconds, printerName, influxUrl);
pS.startScraper();
