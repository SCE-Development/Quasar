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
   * inkLevel determines and returns the current ink level of a HP p2015dn printer
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
   * @returns Promise with toner capacity in unknown units
   */
  async getTonerCapacity() {
    return await this.executeSNMPRequest([SNMP_OBJECT_IDS.TONER_CAPACITY]);
  }

  /**
   * getCurrentTonerLevel makes a snmp query against toner level OID and returns value
   * @returns {Promise} Promise with current toner level in unknown units
   */
  async getCurrentTonerLevel() {
    return await this.executeSNMPRequest([
      SNMP_OBJECT_IDS.CURRENT_TONER_LEVEL,
    ]);
  }
  /**
   * executreSNMPRequest makes a snmp query against the given OID
   * @param {String} objectIdentifier OID to query
   * @returns value corresponding to OID, or false on error
   */
  async getPagesPrinted() {
    return await this.executeSNMPRequest([
      SNMP_OBJECT_IDS.PAGES_PRINTED,
    ]);
  }

  /**
   * executreSNMPRequest makes a snmp query against the given OID
   * @param {String} objectIdentifier OID to query
   * @returns value corresponding to OID, or false on error
   */
  async getMacAddy() {
    return await this.executeSNMPRequest([
      SNMP_OBJECT_IDS.MAC_ADDY,
    ]);
  }

  /**
   * executreSNMPRequest makes a snmp query against the given OID
   * @param {String} objectIdentifier OID to query
   * @returns value corresponding to OID, or false on error
   */
  async getSerialNumber() {
    return await this.executeSNMPRequest([
      SNMP_OBJECT_IDS.SERIAL_NUMBER,
    ]);
  }

  /**
   * executreSNMPRequest makes a snmp query against the given OID
   * @param {String} objectIdentifier OID to query
   * @returns value corresponding to OID, or false on error
   */
  async getModelNumber() {
    return await this.executeSNMPRequest([
      SNMP_OBJECT_IDS.MODEL_NUMBER,
    ]);
  }

  /**
   * executreSNMPRequest makes a snmp query against the given OID
   * @param {String} objectIdentifier OID to query
   * @returns value corresponding to OID, or false on error
   */
  async getMemorySize() {
    return await this.executeSNMPRequest([
      SNMP_OBJECT_IDS.MEMORY_SIZE,
    ]);
  }

  /**
   * executreSNMPRequest makes a snmp query against the given OID
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


module.exports = {HPp2015dn};
