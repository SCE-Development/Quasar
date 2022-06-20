const snmp = require('net-snmp');


// see https://github.com/remetremet/SNMP-OIDs/blob/master/OIDs/Printer-HP-LaserJet-P2055.md
const SNMP_OBJECT_IDS = {
  TONER_CAPACITY: '1.3.6.1.2.1.43.11.1.1.8.1.1',
  CURRENT_TONER_LEVEL: '1.3.6.1.2.1.43.11.1.1.9.1.1',
  PAGES_PRINTED: '1.3.6.1.2.1.43.10.2.1.4.1.1',
  DEVICE_UPTIME: '1.3.6.1.2.1.1.3.0',
  MAC_ADDY: '1.3.6.1.2.1.2.2.1.6.1',
  SERIAL_NUMBER: '1.3.6.1.2.1.43.5.1.1.17.1',
  MODEL_NUMBER: '1.3.6.1.2.1.25.3.2.1.3.1',
  MEMORY_SIZE: '1.3.6.1.2.1.25.2.3.1.5.1',
  MEMORY_USED: '1.3.6.1.2.1.25.2.3.1.6.1'
};


class HpLaserJetP2015 {
  constructor(printerIP) {
    this.printerIP = printerIP;
  }

  /**
   * getInkLevel determines and returns the current ink level of a HP p2015dn printer
   * when the current toner level is queried with SNMP, the printer will return a number such as 1833.
   * @param {String} printerIP IP address of printer to query
   * @returns Promise with current ink level of printer in % of capacity
   */
  async getInkLevel() {
    const currentLevel = await this.getCurrentTonerLevel();
    const capacity = await this.getTonerCapacity();

    if (currentLevel && capacity) {
      return (currentLevel / capacity) * 100;
    }

    return false;
  }

  /**
   * getTonerCapacity makes a snmp query against toner capacity OID and returns value
   * when the toner capacity is queried with SNMP, the printer will return a number such as 2620.
   * @returns Promise with toner capacity in unknown units
   */
  async getTonerCapacity() {
    return await this.executeSNMPRequest([SNMP_OBJECT_IDS.TONER_CAPACITY]);
  }

  /**
   * getCurrentTonerLevel makes a snmp query against toner level OID and returns value
   * when the current toner level is queried with SNMP, the printer will return a number such as 1833.
   * @returns {Promise} Promise with current toner level in unknown units
   */
  async getCurrentTonerLevel() {
    return await this.executeSNMPRequest([
      SNMP_OBJECT_IDS.CURRENT_TONER_LEVEL,
    ]);
  }
  /**
   * getPagesPrinted makes a snmp query against the pages printed OID and returns the total pages printed
   * when the pages printed is queried with SNMP, the printer will return an number such as 52329.
   * @param {String} objectIdentifier OID to query
   * @returns value corresponding to OID, or false on error
   */
  async getPagesPrinted() {
    return await this.executeSNMPRequest([
      SNMP_OBJECT_IDS.PAGES_PRINTED,
    ]);
  }

  /**
   * getMacAddy makes a snmp query against the Mac Address OID and returns mac address.
   * when the mac adress is queried with SNMP, it returns ----
   * @param {String} objectIdentifier OID to query
   * @returns value corresponding to OID, or false on error
   */
  async getMacAddy() {
    return await this.executeSNMPRequest([
      SNMP_OBJECT_IDS.MAC_ADDY,
    ]);
  }

  /**
   * getSerialNumber makes a snmp query against the Serial Number OID and returns the serial number
   * when the serial number is queried with SNMP, the printer will return a number such as, .
   * @param {String} objectIdentifier OID to query
   * @returns value corresponding to OID, or false on error
   */
  async getSerialNumber() {
    return await this.executeSNMPRequest([
      SNMP_OBJECT_IDS.SERIAL_NUMBER,
    ]);
  }

  /**
   * getModelNumber makes a snmp query against the Model Number OID and returns the model Number of the Printer
   * when the model number is queried with SNMP, the printer will return the name such as, HP LaserJet P2015 Series
   * @param {String} objectIdentifier OID to query
   * @returns value corresponding to OID, or false on error
   */
  async getModelNumber() {
    return await this.executeSNMPRequest([
      SNMP_OBJECT_IDS.MODEL_NUMBER,
    ]);
  }

  /**
   * getMemorySize makes a snmp query against the Memory Size OID and returns the memory size of the Printer
   * when the memory size is queried with SNMP, the printer will return the memory size, such as, 301989872
   * @param {String} objectIdentifier OID to query
   * @returns value corresponding to OID, or false on error
   */
  async getMemorySize() {
    return await this.executeSNMPRequest([
      SNMP_OBJECT_IDS.MEMORY_SIZE,
    ]);
  }

  /**
   * getMemoryUsed makes a snmp query against the Memory Used OID and returns the memory used of the Printer
   * when the memory used is queried with SNMP, the printer will return the memory used, such as, 18249829
   * @param {String} objectIdentifier OID to query
   * @returns value corresponding to OID, or false on error
   */
  async getMemoryUsed() {
    return await this.executeSNMPRequest([
      SNMP_OBJECT_IDS.MEMORY_USED,
    ]);
  }

  /**
   * executreSNMPRequest makes a snmp query against the given OID
   * @param {String} objectIdentifier OID to query
   * @returns value corresponding to OID, or false on error
   */
  async executeSNMPRequest(objectIdentifier) {
    return new Promise((resolve) => {
      const session = snmp.createSession(this.printerIP, 'public');
      try {
        session.get(objectIdentifier, function (error, result) {
          if (error) {
            resolve(false);
          } else {
            resolve(result[0].value);
          }
          session.close();
        });

        session.trap(snmp.TrapType.LinkDown, function (error) {
          if (error) {
            resolve(false);
          }
        });
      } catch (e) {
        resolve(false);
      }
    });
  }
  

}


module.exports = {HpLaserJetP2015};
