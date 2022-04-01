const snmp = require('net-snmp');

async function inkLevel(printer) {
  const currentLevel = await getCurrentTonerLevel(printer);
  const capacity = await getTonerCapacity(printer);

  return (currentLevel / capacity) * 100;
}

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

