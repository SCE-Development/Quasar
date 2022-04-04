const snmp = require('net-snmp');
const SNMP_OBJECT_IDS = {
  TONER_CAPACITY: '1.3.6.1.2.1.43.11.1.1.8.1.1',
  CURRENT_TONER_LEVEL: '1.3.6.1.2.1.43.11.1.1.9.1.1',
};

/**
 * inkLevel determines and returns the current ink level of a HP p2015dn printer
 * @param {String} printerIP IP address of printer to query
 * @returns Promise with current ink level of printer in % of capacity
 */
async function inkLevel(printerIP) {
  const currentLevel = await getCurrentTonerLevel(printerIP);
  console.log(currentLevel);
  const capacity = await getTonerCapacity(printerIP);
  console.log(capacity);

  if (currentLevel && capacity) {
    return (currentLevel / capacity) * 100;
  }

  return false;
}

/**
 * getTonerCapacity makes snmp query against toner capacity OID and returns value
 * @param {String} printerIP IP address of printer to query
 * @returns Promise with toner capacity in unknown units
 */
async function getTonerCapacity(printerIP) {
  await executeSNMPRequest(printerIP, [SNMP_OBJECT_IDS.TONER_CAPACITY]);
}
/*
function getTonerCapacity(printer) {
  return new Promise((resolve) => {
    const session = snmp.createSession(printer, 'public');

    const oids = ['1.3.6.1.2.1.43.11.1.1.8.1.1'];

    session.get(oids, function (error, varbinds) {
      if (error) {
        console.error(error);
      } else {
        resolve(varbinds[0].value);
      }
      session.close();
    });

    session.trap(snmp.TrapType.LinkDown, function (error) {
      if (error) {
        console.error(error);
      }
    });
  });
}*/

/**
 * getCurrentTonerLevel makes snmp query against toner level OID and returns value
 * @param {String} printer IP address of printer to query
 * @returns Promise with current toner level in unknown units
 */

async function getCurrentTonerLevel(printerIP) {
  console.log(printerIP);
  await executeSNMPRequest(printerIP, [SNMP_OBJECT_IDS.CURRENT_TONER_LEVEL]);
}

/*
function getCurrentTonerLevel(printer) {
  return new Promise((resolve) => {
    const session = snmp.createSession(printer, 'public');

    const oids = ['1.3.6.1.2.1.43.11.1.1.9.1.1'];

    session.get(oids, function (error, varbinds) {
      if (error) {
        console.error(error);
      } else {
        resolve(varbinds[0].value);
      }
      session.close();
    });

    session.trap(snmp.TrapType.LinkDown, function (error) {
      if (error) {
        console.error(error);
      }
    });
  });
}
*/

async function executeSNMPRequest(printerIP, objectIdentifier) {
  return new Promise((resolve) => {
    const session = snmp.createSession(printerIP, 'public');
    try {
      session.get(objectIdentifier, function (error, result) {
        if (error) {
          resolve(false);
        } else {
          console.log(result[0].value);
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

module.exports = { inkLevel, getCurrentTonerLevel, getTonerCapacity };
