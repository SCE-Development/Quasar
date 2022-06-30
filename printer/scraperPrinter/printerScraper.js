const fetch = require('node-fetch');
const logger = require('../logger.js');
const {HpLaserJetP2015} = require('../snmp.js');
let temp = 55;
class PrinterScraper {
  constructor(printerIP, intervalSeconds, printerName, influxBaseUrl){
    this.stat = new HpLaserJetP2015(printerIP);
 
    if(!printerIP) {
      throw new Error('printerIP must be set! got value', printerIP);
    }
    if(!intervalSeconds) {
      throw new Error('intervalSeconds must be set! got value', intervalSeconds);
    }
    if(!printerName) {
      throw new Error('printerName must be set! got value', printerName);
    }
    if(!influxBaseUrl) {
      throw new Error('printerIP must be set! got value', influxBaseUrl);
    }
    this.printerIP = printerIP;
    this.intervalSeconds = intervalSeconds;
    this.printerName = printerName;
    this.influxBaseUrl = influxBaseUrl;
  }
  /**
    * creates database for influx called quasar_data, incase it doesnt exist
    */
  async initializeInfluxDb() {
    logger.warn('Creating influx Database called quasar_data if not created already');
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
    * gets the Data that can be received from the printer.
    * returns an object with the values being in the format to be writeable to influxDB.
    * @returns an object, snmpData
    */
  async getSnmpData(){
    const inkLevel = await this.stat.getInkLevel();
    const macAddy = await this.stat.getMacAddy();
    const currentTonerLevel = await this.stat.getCurrentTonerLevel();
    const memorySize = await this.stat.getMemorySize();
    const memoryUsed = await this.stat.getMemoryUsed();
    const pagesPrinted = await this.stat.getPagesPrinted();
    const serialNumber = await this.stat.getSerialNumber();
    const modelNumber = await this.stat.getModelNumber();
    let snmpData = {
      inkLevel,
      macAddy,
      currentTonerLevel,
      memorySize,
      memoryUsed,
      pagesPrinted,
      serialNumber,
      modelNumber,
    };
    return await snmpData;
  }
  /**
    * creates a string from snmpData to pass to influxDB
    * @param {snmpData} object
    * @returns string object bodyData, to pass to body for influxDB
    */
  formatForInflux(){
    logger.info('Formatted SNMP data');
    let bodyData = 'laserJet,tag=CNB9M04409 inkLevel=69.9618320610687' + '\n';
    bodyData += 'laserJet,tag=CNB9M04409 macAddy=" "'  + '\n';
    bodyData += 'laserJet,tag=CNB9M04409 currentTonerLevel=1833' + '\n';
    bodyData += 'laserJet,tag=CNB9M04409 memorySize=301989872' + '\n';
    bodyData += 'laserJet,tag=CNB9M04409 memoryUsed=18249829' + '\n';
    bodyData += `laserJet,tag=CNB9M04409 pagesPrinted=${temp += 1}` + '\n';  
    bodyData += 'laserJet,tag=CNB9M04409 serialNumber="CNB9M04409"' + '\n';  
    bodyData += 'laserJet,tag=CNB9M04409 modelNumber=" "'+ '\n'; 
    bodyData += 'laserJet,tag=CNB9M04409 tonerCapacity=2620';  
    logger.warn('This was Sent \n' + bodyData);
    return bodyData;
  }
   
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
    * @returns the response that was given by the write to influx db
    */
  async handleScrape(globalThis){
    // let bodyData = await globalThis.formatForInflux(await globalThis.getSnmpData());
    let bodyData = await globalThis.formatForInflux();
    globalThis.writeToInflux(bodyData);
  }
  // Start the query
  startScraper(){
    console.log(this.intervalSeconds, '/query');
    logger.warn(String(`Starting Query with Interval ${this.intervalSeconds} seconds`));
    setInterval(() => {
      this.handleScrape(this);
    }, this.intervalSeconds * 1000);
  }
}
module.exports = {PrinterScraper};
 
 
