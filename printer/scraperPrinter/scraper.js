const rawArgs = process.argv.slice(2);
if(rawArgs.length != 6)
{
  throw new Error('Incorrect Length');
}
let printerIP = '';
let intervalSeconds = 0;
let stat = ''
let printerName = ''
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
    case '--printer_name':
      printerName = rawArgs[i + 1];
    default:
      throw new Error('Check Argument: ' + rawArgs[i]);
  }
}

// minimum seconds due to data receiving speed
if(intervalSeconds < 60)
{
  console.log('interval seconds has been changed to 60 seconds');
  intervalSeconds = 60;
}



/**
 * fix the object we are querying
 * dont hardcode ip
 * database name
 * left or right printer?
 * moving code to its own dir
 * take a look at arg parsing
 */
