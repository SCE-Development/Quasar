const snmp = require('net-snmp');
const SNMP_OBJECT_IDS = {
  TONER_CAPACITY: '1.3.6.1.2.1.43.11.1.1.8.1.1',
  CURRENT_TONER_LEVEL: '1.3.6.1.2.1.43.11.1.1.9.1.1',
};

class HPp2015dn {
  /**
   * inkLevel determines and returns the current ink level of a HP p2015dn printer
   * @param {String} printerIP IP address of printer to query
   * @returns Promise with current ink level of printer in % of capacity
   */
  async inkLevel(printerIP) {
    const currentLevel = await this.getCurrentTonerLevel(printerIP);
    const capacity = await this.getTonerCapacity(printerIP);

    if (currentLevel && capacity) {
      return (currentLevel / capacity) * 100;
    }

    return false;
  }

  /**
   * getTonerCapacity makes a snmp query against toner capacity OID and returns value
   * @param {String} printerIP IP address of printer to query
   * @returns Promise with toner capacity in unknown units
   */
  async getTonerCapacity(printerIP) {
    return await this.executeSNMPRequest(printerIP, [SNMP_OBJECT_IDS.TONER_CAPACITY]);
  }

  /**
   * getCurrentTonerLevel makes a snmp query against toner level OID and returns value
   * @param {String} printerIP IP address of printer to query
   * @returns {Promise} Promise with current toner level in unknown units
   */
  async getCurrentTonerLevel(printerIP) {
    return await this.executeSNMPRequest(printerIP, [
      SNMP_OBJECT_IDS.CURRENT_TONER_LEVEL,
    ]);
  }

  /**
   * executreSNMPRequest makes a snmp query against the given OID
   * @param {String} printerIP IP address of printer to query
   * @param {String} objectIdentifier OID to query
   * @returns value corresponding to OID, or false on error
   */
  async executeSNMPRequest(printerIP, objectIdentifier) {
    return new Promise((resolve) => {
      const session = snmp.createSession(printerIP, 'public');
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

