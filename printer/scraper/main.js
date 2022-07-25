const logger = require('../../util/logger.js');
const { InfluxHandler } = require('./InfluxHandler');
const { HpLaserJetP2015 } = require('../snmp.js');

function printUsage() {
  console.log('usage: node main.js --printer_ip <ip address>,<ip address>\
  --fetch_interval_seconds <seconds>\
  --printer_name <name>,<name>\
  --influx_url <url>');
}

function main() {
  const rawArgs = process.argv.slice(2);

  if (rawArgs.length != 8) {
    return printUsage();
  }
  console.log(rawArgs)
  let printerIPs = [];
  let intervalSeconds = 0;
  let printerNames = [];
  let influxUrl = '';

  // perform argument checks before continuing with program
  for (let i = 0; i < rawArgs.length; i += 2) {
    switch (rawArgs[i]) {
      case '--printer_ips':
        printerIPs[0] = rawArgs[i + 1];
        if(rawArgs[i + 1].includes(','))
        {
          for(let j  = 0; j < rawArgs[i + 1].split(',').length; j++)
          {
            printerIPs[j] = rawArgs[i + 1].split(',')[j];
          }
        }
        break;
      case '--fetch_interval_seconds':
        intervalSeconds = rawArgs[i + 1];
        break;
      case '--printer_names':
        printerNames[0] = rawArgs[i + 1];
        if(rawArgs[i + 1].includes(','))
        {
          for(let j  = 0; j < rawArgs[i + 1].split(',').length; j++)
          {
            printerNames[j] = rawArgs[i + 1].split(',')[j];
          }
        }
        break;
      case '--influx_url':
        influxUrl = rawArgs[i + 1];
        break;
      default:
        return printUsage();
    }
  }

  let snmpArray = [];
  let influxHandlerArray = [];

  for(let i = 0; i < printerIPs.length; i++){
    let ipAddress = printerIPs[i];
    let theName = printerNames[i];
    snmpArray[i] = new HpLaserJetP2015(ipAddress);
    influxHandlerArray[i] = new InfluxHandler(influxUrl, theName);
    logger.info(`Printer IP: ${ipAddress}\
            Interval: ${intervalSeconds}\
            Printer Name: ${theName}\
            Influx URL: ${influxUrl}`);
  }

  //make the db
  influxHandlerArray[0].initializeInfluxDb();

  setInterval(async () => {
    for(let i = 0; i < printerIPs.length; i++){
      const bodyData = await snmpArray[i].getSnmpData();
      const dataForInflux = await influxHandlerArray[i].formatForInflux(bodyData);
      await influxHandlerArray[i].writeToInflux(dataForInflux); 
      console.log("WITH IP ADDRESS: " + printerIPs[i]);
    } 
  }, intervalSeconds * 1000);
}

main();
