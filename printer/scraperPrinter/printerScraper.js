const fetch = require('node-fetch')
const logger = require('../logger.js')
const {HpLaserJetP2015} = require('../snmp.js');
class PrinterScraper {
    constructor(printerIP, intervalSeconds, printerName, influxBaseUrl){
        this.stat = new HpLaserJetP2015(printerIP);

        if(!printerIP) {
          throw new Error("printerIP must be set! got value", printerIP)
        }
        if(!intervalSeconds) {
            throw new Error("intervalSeconds must be set! got value", intervalSeconds)
        }
        if(!printerName) {
            throw new Error("printerName must be set! got value", printerName)
        }
        if(!influxBaseUrl) {
            throw new Error("printerIP must be set! got value", influxBaseUrl)
        }
        this.printerIP = printerIP;
        this.intervalSeconds = intervalSeconds
        this.printerName = printerName
        this.influxBaseUrl = influxBaseUrl
    }
    /**
     * creates database for influx called quasar_data, incase it doesnt exist
     */
    async initializeInfluxDb() {
        logger.warn("Creating influx Database called quasar_data if not created already")
      fetch(`${this.influxBaseUrl}/query`,{
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: 'q=CREATE DATABASE "quasar_data"'
     });
    }
  
  
    /**
     * gets the Data that can be received from the printer.
     * returns an object with the values being in the format to be writeable to influxDB.
     * @returns an object, snmpData
     */
    async getSnmpData(){
        logger.info("Got SNMP Data");
      let snmpData = {
        inkLevel: await this.stat.getInkLevel(),
        macAddy: await this.stat.getMacAddy(),
        currentTonerLevel: await this.stat.getCurrentTonerLevel(),
        memorySize: await this.stat.getMemorySize(),
        memoryUsed: await this.stat.getMemoryUsed(),
        pagesPrinted: await this.stat.getPagesPrinted(),
        serialNumber: await this.stat.getSerialNumber(),
        modelNumber: await this.stat.getModelNumber(),
      };
      return snmpData;
    }
    /**
     * creates a string from snmpData to pass to influxDB
     * @param {snmpData} object 
     * @returns string object bodyData, to pass to body for influxDB
     */
    formatForInflux(snmpData){
        logger.info("Formatted SNMP data");
      let bodyData = 'laserJet inkLevel=' + String(snmpData.inkLevel);
      bodyData += '\nlaserJet macAddy=' + String(snmpData.macAddy);
      bodyData += '\nlaserJet currentTonerLevel=' + String(snmpData.currentTonerLevel);
      bodyData += '\nlaserJet memorySize=' + String(snmpData.memorySize);
      bodyData += '\nlaserJet memoryUsed=' + String(snmpData.memoryUsed);
      bodyData += '\nlaserJet pagesPrinted=' + String(snmpData.pagesPrinted);
      bodyData += '\nlaserJet serialNumber=' + String(snmpData.serialNumber);
      bodyData += '\nlaserJet modelNumber=' + String(snmpData.modelNumber);
      bodyData += '\nlaserJet printerName=' + this.printerName;
      return bodyData;
    }
    
    async writeToInflux(bodyData){  
        logger.info("Writing to influxDB");
        try {
            const response = await fetch(`${this.influxBaseUrl}/write?db=mydb&precision=s`, {
                body: bodyData,
                headers: {
                  'Content-Type': 'application/x-www-form-urlencoded'
                },
                method: 'POST'
              });
          } catch (error) {
            logger.error("Error Writing to influx.")
          }
      return response
    }
  
  
    /**
     * writes the data gotten to influxDB, return should not contain 'x-influxdb-error' 
     * otherwise there was a write error. 
     * @returns the response that was given by the write to influx db
     */
    async handleScrape(){
      let bodyData = await this.formatForInflux(await this.getSnmpData());
      return await this.writeToInflux(bodyData);
    }
  
    //Start the query
    startScraper(){
        logger.warn(String(`Starting Query with Interval ${this.intervalSeconds} seconds`))
      setInterval(this.handleScrape, this.intervalSeconds * 1000);
    }
  }
  
  module.exports = {PrinterScraper};
  