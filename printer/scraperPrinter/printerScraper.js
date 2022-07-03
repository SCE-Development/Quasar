const logger = require('../logger.js');
const {InfluxHandler} = require('./InfluxHandler');

class PrinterScraper {
  constructor(printerIP, intervalSeconds, printerName, influxBaseUrl){
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
    this.toInflux = new InfluxHandler(printerIP, influxBaseUrl, printerName);
 
    this.printerIP = printerIP;
    this.intervalSeconds = intervalSeconds;
    this.printerName = printerName;
    this.influxBaseUrl = influxBaseUrl;
    this.influxHandler;
  }
 
  /**
  * Starts the Scraper at the desired interval
  */
  startScraper(){
    this.toInflux.initializeInfluxDb();
    logger.warn(String(`Starting Query with Interval ${this.intervalSeconds} seconds`));
    setInterval(() => {
      this.toInflux.handleScrape(this);
    }, this.intervalSeconds * 1000);
  }
}
module.exports = {PrinterScraper};
