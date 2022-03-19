const snmp = require('net-snmp');
const config = require('../config/config.json');
const { RIGHT_PRINTER_IP, LEFT_PRINTER_IP } = config;
let session;

function inkLevel(printer) {
  return new Promise((resolve) => {
    if (printer == 'right') {
      session = snmp.createSession(RIGHT_PRINTER_IP, 'public');
    } else if (printer == 'left') {
      session = snmp.createSession(LEFT_PRINTER_IP, 'public');
    }

    const oids = ['1.3.6.1.2.1.43.11.1.1.8.1.1', '1.3.6.1.2.1.43.11.1.1.9.1.1'];

    session.get(oids, function (error, varbinds) {
      if (error) {
        console.error(error);
      } else {
        resolve((varbinds[1].value / varbinds[0].value) * 100);
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

module.exports = { inkLevel };
