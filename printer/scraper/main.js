const logger = require('../../util/logger.js');
const { InfluxHandler } = require('./InfluxHandler');
const { HpLaserJetP2015 } = require('../snmp.js');
const client = require('prom-client');
const express = require('express');
const app = express();
let register = new client.Registry();

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
  let printerIPs = [];
  let intervalSeconds = 0;
  let printerNames = [];
  let influxUrl = '';

  // perform argument checks before continuing with program
  for (let i = 0; i < rawArgs.length; i += 2) {
    switch (rawArgs[i]) {
      case '--printer_ips':
        printerIPs[0] = rawArgs[i + 1].replace(/["']/g, '');
        if(rawArgs[i + 1].includes(','))
        {
          for(let j  = 0; j < rawArgs[i + 1].split(',').length; j++)
          {
            printerIPs[j] = rawArgs[i + 1].split(',')[j].replace(/["']/g, '');
          }
        }
        break;
      case '--fetch_interval_seconds':
        intervalSeconds = rawArgs[i + 1];
        break;
      case '--printer_names':
        printerNames[0] = rawArgs[i + 1].replace(/["']/g, '');
        if(rawArgs[i + 1].includes(','))
        {
          for(let j  = 0; j < rawArgs[i + 1].split(',').length; j++)
          {
            printerNames[j] = rawArgs[i + 1].split(',')[j].replace(/["']/g, '');
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
  let gaugeArrayLatency = [];
  let gaugeArrayLastSeen = [];

  for(let i = 0; i < printerIPs.length; i++){
    let ipAddress = printerIPs[i];
    let theName = printerNames[i];
    snmpArray[i] = new HpLaserJetP2015(ipAddress);
    influxHandlerArray[i] = new InfluxHandler(influxUrl, theName);
    logger.info(`Printer IP: ${ipAddress}\
            Interval: ${intervalSeconds}\
            Printer Name: ${theName}\
            Influx URL: ${influxUrl}`);
    gaugeArrayLatency[i] = new client.Gauge({
      name: `time_spent_querying_data_${theName}`,
      help: `time_gauge_help_${theName}`,
    });
    gaugeArrayLastSeen[i] = new client.Gauge({
      name: `${theName}_last_seen`,
      help: `${theName}_last_seen_help`,
    });
    register.registerMetric(gaugeArrayLatency[i]);
    register.registerMetric(gaugeArrayLastSeen[i]);
  }

  register.setDefaultLabels ({
    app: 'printer-temp'
  });

  client.collectDefaultMetrics({ register });


  app.get('/metrics', async (request, response) => {
    response.setHeader('Content-Type', register.contentType);
    response.end(await register.metrics());
  });
  
  app.listen(5000, () =>{
    console.log('Started server on port 5000');
  });


  // make the db
  influxHandlerArray[0].initializeInfluxDb();

  setInterval(async () => {
    for(let i = 0; i < printerIPs.length; i++){
      const end = gaugeArrayLatency[i].startTimer();
      gaugeArrayLastSeen[i].set(Date.now());
      const bodyData = await snmpArray[i].getSnmpData();
      end();
      const dataForInflux = await influxHandlerArray[i].formatForInflux(bodyData);
      await influxHandlerArray[i].writeToInflux(dataForInflux); 
    } 
  }, intervalSeconds * 1000);
}

main();
