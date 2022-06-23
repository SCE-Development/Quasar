const {HpLaserJetP2015} = require("./snmp.js")
const rawArgs = process.argv.slice(2);
//perform argumeent checks before continuing with program
if(rawArgs.length != 4)
{
    throw new Error("Incorrect Length")
}
let printerIP = "";
let intervalSeconds = 0;
//perform argument checks before continuing with program
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

//minimum seconds due to data receiving speed
if(intervalSeconds < 60)
{
    console.log("interval seconds has been changed to 60 seconds");
    intervalSeconds = 60;
}


/**
 * gets the Data that can be received from the printer.
 * returns an object with the values being in the format to be writeable to influxDB.
 * @returns an object, snmpData
 */
async function getSnmpData(){
    snmpData = {
        'Ink Level: ': 'peepoo9,mytag=1 inkLevel=' + await stat.getInkLevel(),
        'Mac Addy: ': 'peepoo9,mytag=1 macAddy=' + String(await stat.getMacAddy()),
        'Current Toner Level: ': 'peepoo9,mytag=1 currentTonerLevel=' + await stat.getCurrentTonerLevel(),
        'Memory Size: ': 'peepoo9,mytag=1 memSize=' + await stat.getMemorySize(),
        'Memory Used: ': 'peepoo9,mytag=1 memUsed=' + await stat.getMemoryUsed(),
        'Pages Printed: ': 'peepoo9,mytag=1 pagesPrinted=' + await stat.getPagesPrinted(),
        'Serial Number: ': 'peepoo9,mytag=1 serialNum=' + String(await stat.getSerialNumber()),
        'Model Number: ': 'peepoo9,mytag=1 modelNum=' + String(await stat.getModelNumber())
    };
    return await snmpData;
}
/**
 * creates a string from snmpData to pass to influxDB
 * @param {snmpData} snmpData 
 * @returns string object bodyData, to pass to body for influxDB
 */
function formatForInflux(snmpData){
    let bodyData = String(snmpData['Ink Level: ']);
    bodyData += "\n" + String(snmpData['Memory Size: ']);
    bodyData += "\n" + String(snmpData['Current Toner Level: ']);
    bodyData += "\n" + String(snmpData['Pages Printed: ']);
    bodyData += "\n" + String(snmpData['Serial Number: ']);
    bodyData += "\n" + String(snmpData['Memory Used: ']);
    console.log(bodyData);
    return bodyData
}

/**
 * writes the data gotten to influxDB, return should not contain 'x-influxdb-error' 
 * otherwise there was a write error. 
 * @returns the response that was given by the write to influx db
 */
async function writeToInflux(){
    let bodyData = await formatForInflux(await getSnmpData());
    const response = await fetch("http://localhost:8086/write?db=mydb&precision=s", {
        body: bodyData,
        headers: {
        "Content-Type": "application/x-www-form-urlencoded"
        },
        method: "POST"
    })
    console.log("queried :>")
    return await response;
}
console.log("Starting Query, Ctrl+c to quit.")
setInterval(writeToInflux, intervalSeconds * 1000);
