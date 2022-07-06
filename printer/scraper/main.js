const logger = require('../../util/logger.js');
const { InfluxHandler } = require('./InfluxHandler');
const { HpLaserJetP2015 } = require('../snmp.js');

function printUsage() {
  console.log('usage: node main.js --printer_ip <ip address> --fetch_interval_seconds <seconds>\
  --printer_name <name> --influx_url <url>');
}

function main() {
  const rawArgs = process.argv.slice(2);

  if (rawArgs.length != 8) {
    return printUsage();
  }

  let printerIP = '';
  let intervalSeconds = 0;
  let printerName = '';
  let influxUrl = '';

  // perform argument checks before continuing with program
  for (let i = 0; i < rawArgs.length; i += 2) {
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
        return printUsage();
    }
  }

  logger.info(`Printer IP: ${printerIP}\
            Interval: ${intervalSeconds}\
            Printer Name: ${printerName}\
            Influx URL: ${influxUrl}`);

  let snmpHandler = new HpLaserJetP2015(printerIP);
  let influxHandler = new InfluxHandler(influxUrl, printerName);
  setInterval(async () => {
    const bodyData = await snmpHandler.getSnmpData();
    const dataForInflux = await influxHandler.formatForInflux(bodyData);
    await influxHandler.writeToInflux(dataForInflux);
  }, intervalSeconds * 1000);
}

main();
