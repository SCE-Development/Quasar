const fetch = require('node-fetch');
const logger = require('../../util/logger.js');


class InfluxHandler {
  constructor(influxBaseUrl, printerName) {
    this.influxBaseUrl = influxBaseUrl;
    this.printerName = printerName;
  }

  /**
  * Creates DataBase by the name of quasar_data if not made already
  */
  async initializeInfluxDb() {
    logger.info('Creating influx Database called quasar_data if not created already');
    try {
      await fetch(`${this.influxBaseUrl}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: 'q=CREATE DATABASE "quasar_data"'
      });
    } catch (error) {
      logger.error('Error Creating Database!');
    }
  }

  /**
    * creates a string from snmpData to pass to influxDB
    * @param {snmpData} object
    * @returns string object bodyData, to pass to body for influxDB
    */
  formatForInflux(snmpData) {
    logger.info('Formatted SNMP data');
    let bodyData = '';
    Object.keys(snmpData).forEach(key => {
      let value = snmpData[key];
      if (typeof value === 'string') {
        value = `"${value}"`;
      }
      bodyData += `laserJet,tag=${this.printerName} ${key}=${value}\n`;
    });
    return bodyData;
  }

  /**
  * Writes to influx with bodyData parameter that is receieved.
  * @param {bodyData} bodyData
  */
  async writeToInflux(bodyData) {
    logger.info('Writing to influxDB');
    try {
      const response = await fetch(`${this.influxBaseUrl}/write?db=quasar_data`, {
        body: bodyData,
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        method: 'POST'
      });
      return await response;
    } catch (error) {
      logger.error('Error Writing to influx.');
    }
  }
}

module.exports = { InfluxHandler };
