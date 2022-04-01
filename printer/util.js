const snmp = require('net-snmp');

/**
 * inkLevel determines and returns the current ink level of a HP p2015dn printer
 * @param {String} printer IP address of printer to query
 * @returns {Promise} Promise with current ink level of the printer in % of capacity
 */
async function inkLevel(printer) {
  const currentLevel = await getCurrentTonerLevel(printer);
  const capacity = await getTonerCapacity(printer);

  return (currentLevel / capacity) * 100;
}

/**
 * getTonerCapacity makes snmp query against toner capacity OID and returns value
 * @param {String} printer IP address of printer to query
 * @returns {Promise} Promise with toner capacity in unknown units
 */
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
}

/**
 * getCurrentTonerLevel makes snmp query against toner level OID and returns value
 * @param {String} printer IP address of printer to query
 * @returns {Promise} Promise with current toner level in unknown units
 */
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

module.exports = { inkLevel, getCurrentTonerLevel, getTonerCapacity };
