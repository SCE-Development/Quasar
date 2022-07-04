const logger = require('../logger.js');
const { InfluxHandler } = require('./InfluxHandler');
const { HpLaserJetP2015 } = require('../snmp.js');

class PrinterScraper {
  constructor(printerIP, intervalSeconds, printerName, influxBaseUrl) {
    if (!printerIP) {
      throw new Error('printerIP must be set! got value', printerIP);
    }
    if (!intervalSeconds) {
      throw new Error('intervalSeconds must be set! got value', intervalSeconds);
    }
    if (!printerName) {
      throw new Error('printerName must be set! got value', printerName);
    }
    if (!influxBaseUrl) {
      throw new Error('printerIP must be set! got value', influxBaseUrl);
    }
    this.influxHandler = new InfluxHandler(influxBaseUrl, printerName);
    this.snmpHandler = new HpLaserJetP2015(printerIP);

    this.intervalSeconds = intervalSeconds;
  }


  /**
   * writes the data gotten to influxDB, return should not contain 'x-influxdb-error'
   * otherwise there was a write error.
   */
  async handleScrape(globalThis) {
    const snmpDataFromPrinter = await globalThis.snmpHandler.getSnmpData();
    const dataForInflux = await globalThis.influxHandler.formatForInflux(snmpDataFromPrinter);
    globalThis.influxHandler.writeToInflux(dataForInflux);
  }

  /**
  * Starts the Scraper at the desired interval
  */
  startScraper() {
    this.influxHandler.initializeInfluxDb();
    logger.warn(String(`Starting Query with Interval ${this.intervalSeconds} seconds`));
    setInterval(() => {
      this.handleScrape(this);
    }, this.intervalSeconds * 1000);
  }
}

module.exports = { PrinterScraper };
