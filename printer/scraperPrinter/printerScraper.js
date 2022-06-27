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
      console.log(snmpData, "ASDFASDFASDF")
      // logger.info(snmpData);
      return snmpData;
    }
    /**
     * creates a string from snmpData to pass to influxDB
     * @param {snmpData} object 
     * @returns string object bodyData, to pass to body for influxDB
     */
    formatForInflux(snmpData){
        logger.info("Formatted SNMP data");
      let bodyData = 'laserJet,tag=1 inkLevel="' + String(snmpData.inkLevel) + '",';
      // bodyData += 'macAddy="' + String(snmpData.macAddy) + '",';
      // bodyData += 'currentTonerLevel="' + String(snmpData.currentTonerLevel) + '",';
      // bodyData += 'memorySize="' + String(snmpData.memorySize) + '",';
      // bodyData += 'memoryUsed="' + String(snmpData.memoryUsed) + '",';
      // bodyData += 'pagesPrinted="' + String(snmpData.pagesPrinted) + '",';
      // bodyData += 'serialNumber="' + String(snmpData.serialNumber) + '",';
      // bodyData += 'modelNumber="' + String(snmpData.modelNumber) + '",';
      // bodyData += 'printerName="' + this.printerName + '\n"';
      console.log("WHYY ME", bodyData)
      return bodyData;
    }
    
    async writeToInflux(bodyData){  
        logger.info("Writing to influxDB");
        try {
            const response = await fetch(`${this.influxBaseUrl}/write?db=quasar_data`, {
                body: bodyData,
                headers: {
                  'Content-Type': 'application/x-www-form-urlencoded'
                },
                method: 'POST'
              });
              console.log("influx returned", response)
              return response
          } catch (error) {
            logger.error("Error Writing to influx.")
          }
    }
  
  
    /**
     * writes the data gotten to influxDB, return should not contain 'x-influxdb-error' 
     * otherwise there was a write error. 
     * @returns the response that was given by the write to influx db
     */
    async handleScrape(globalThis){
      let bodyData = await globalThis.formatForInflux(await globalThis.getSnmpData());
      globalThis.writeToInflux(bodyData);
    }
  
    //Start the query
    startScraper(){
        logger.warn(String(`Starting Query with Interval ${this.intervalSeconds} seconds`))
      setInterval(() => {
        this.handleScrape(this)
      }, this.intervalSeconds * 1000);
    }
  }
  
  module.exports = {PrinterScraper};
  