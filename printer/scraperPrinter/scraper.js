const {PrinterScraper} = require('./printerScraper');
const rawArgs = process.argv.slice(2);
if(rawArgs.length != 8)
{
  throw new Error('Incorrect Length');
}
let printerIP = '';
let intervalSeconds = 0;
let stat = ''
let printerName = ''
let influx_url = ''
//perform argument checks before continuing with program
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
      influx_url = rawArgs[i + 1];
      break;
    default:
      throw new Error('Check Argument: ' + rawArgs[i]);
  }
}
// minimum seconds due to data receiving speed
/*
if(intervalSeconds < 60)
{
  console.log('interval seconds has been changed to 60 seconds');
  intervalSeconds = 60;
}*/

let pS = new PrinterScraper(printerIP, intervalSeconds, printerName, influx_url)
pS.initializeInfluxDb();
pS.startScraper();
/**
 * fix the object we are querying
 * dont hardcode ip
 * database name
 * left or right printer?
 * moving code to its own dir
 * take a look at arg parsing
 */
