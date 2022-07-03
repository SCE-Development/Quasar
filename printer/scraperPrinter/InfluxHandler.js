const fetch = require('node-fetch');
const {HpLaserJetP2015} = require('../snmp.js');
const logger = require('../../util/logger.js');
class InfluxHandler{
 
  constructor(printerIP, influxBaseUrl, printerName) {
    this.snmpHandler = new HpLaserJetP2015(printerIP);
    this.influxBaseUrl = influxBaseUrl;
    this.printerName = printerName;
  }
 
  /**
  * Creates DataBase by the name of quasar_data if not made already
  */
  async initializeInfluxDb() {
    logger.info('Creating influx Database called quasar_data if not created already');
    try{
      await fetch(`${this.influxBaseUrl}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: 'q=CREATE DATABASE "quasar_data"'
      });
    }catch(error){
      logger.error('Error Creating Database!');
    }
  }
 
  /**
    * creates a string from snmpData to pass to influxDB
    * @param {snmpData} object
    * @returns string object bodyData, to pass to body for influxDB
    */
  formatForInflux(snmpData){
    logger.info('Formatted SNMP data');
    let bodyData = `laserJet,tag=${snmpData.serialNumber} inkLevel=`/
     + String(snmpData.inkLevel) + '\n';
    bodyData += `laserJet,tag=${snmpData.serialNumber} macAddy="`/
      + String(snmpData.macAddy) + '"' + '\n';
    bodyData+=`laserJet,tag=${snmpData.serialNumber} currentTonerLevel=`/
      + String(snmpData.currentTonerLevel)+'\n';
    bodyData += `laserJet,tag=${snmpData.serialNumber} memorySize=`/
      + String(snmpData.memorySize) + '\n';
    bodyData += `laserJet,tag=${snmpData.serialNumber} memoryUsed=`/
      + String(snmpData.memoryUsed) + '\n';
    bodyData += `laserJet,tag=${snmpData.serialNumber} pagesPrinted=`/
      + String(snmpData.pagesPrinted) + '\n';
    bodyData+=`laserJet,tag=${snmpData.serialNumber} serialNumber="`/
      + String(snmpData.serialNumber)+'"'+'\n';
    bodyData += `laserJet,tag=${snmpData.serialNumber} modelNumber="`/
      + String(snmpData.modelNumber) + '"' + '\n';
    bodyData += `laserJet,tag=${snmpData.serialNumber} tonerCapacity=`/
      + String(snmpData.tonerCapacity);
    return bodyData;
  }
  /**
  * Writes to influx with bodyData parameter that is receieved.
  * @param {bodyData} bodyData
  */
  async writeToInflux(bodyData){
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
 
  /**
   * writes the data gotten to influxDB, return should not contain 'x-influxdb-error'
   * otherwise there was a write error.
   */
  async handleScrape(globalThis){
    let bodyData = await this.formatForInflux(await this.snmpHandler.getSnmpData());
    globalThis.toInflux.writeToInflux(bodyData);
  }
}
 
module.exports = {InfluxHandler};
