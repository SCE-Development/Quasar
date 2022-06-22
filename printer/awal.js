const {HpLaserJetP2015} = require("./snmp.js")
const rawArgs = process.argv.slice(2);
if(rawArgs.length != 4)
{
throw new Error("Incorrect Length")
}
let printerIP = "";
let intervalSeconds = 0;
let snmpData = {};
for(let i = 0; i < rawArgs.length; i += 2)
{
switch (rawArgs[i]) {
    case '--printer_ip':
        printerIP = rawArgs[i + 1];
        break;
    case '--fetch_interval_seconds':
        intervalSeconds = rawArgs[i + 1];
        break;
    default:
        throw new Error("Check Argument: " + rawArgs[i]);
}
}
let stat = new HpLaserJetP2015(printerIP);

//if(intervalSeconds < 45) intervalSeconds = 45;

/**
 * 
 * @returns an object, snmpData
 */
async function getSnmpData(){
    snmpData = {
        'Ink Level: ': 'mytag=1 inkLevel=' + await stat.getInkLevel(),
        'Mac Addy: ': 'macAddy=' + String(await stat.getMacAddy()),
        'Current Toner Level: ': 'currentTonerLevel=' + await stat.getCurrentTonerLevel(),
        'Memory Size: ': 'peepoo4,mytag=2 memSize=' + await stat.getMemorySize(),
        'Memory Used: ': 'peepoo4,mytag=3 memUsed=' + await stat.getMemoryUsed(),
        'Pages Printed: ': 'pagesPrinted=' + await stat.getPagesPrinted(),
        'Serial Number: ': 'serialNum=' + String(await stat.getSerialNumber()),
        'Model Number: ': 'modelNum=' + String(await stat.getModelNumber())
    };
    return await snmpData;
}

async function intervalConfirm(){
    console.log(await getSnmpData());
}
/*
let snmpData = {
    'Ink Level: ': 'mytag=1 inkLevel=33',
    'Mac Addy: ': 'macAddy=',
    'Current Toner Level: ': 'currentTonerLevel=',
    'Memory Size: ': 'peepoo2,mytag=2 memSize=31',
    'Memory Used: ': 'peepoo2,mytag=3 memUsed=32',
    'Pages Printed: ': 'pagesPrinted=',
    'Serial Number: ': 'serialNum=',
    'Model Number: ': 'modelNum='
};*/


async function tempDo(){
    await intervalConfirm();
    const response = await fetch("http://localhost:8086/write?db=mydb&precision=s", {
        body: "peepoo4," + snmpData['Ink Level: '] + "\n" + snmpData['Memory Size: '] + "\n" + snmpData['Memory Used: '],
        headers: {
        "Content-Type": "application/x-www-form-urlencoded"
        },
        method: "POST"
    })
    console.log(response);
    return await response;
}

tempDo();
/*
console.log("Starting Query, Ctrl+c to quit.")
setInterval(intervalConfirm, intervalSeconds * 1000);
*/