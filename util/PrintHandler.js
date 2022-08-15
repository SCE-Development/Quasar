const axios = require('axios');
const fs = require('fs');
const exec = require('exec');
const logger = require('./logger');

const { PRINTING } = require('../config/config.json');


function sendRequestToPrinter(options) {
  const { copies, pages, printer, filePath } = options;
  let maybePageRange = '';
  if (pages && pages !== 'NA') {
    maybePageRange = `-P ${pages}`;
  }
  return new Promise((resolve) => {
    exec(
      `lp -n ${copies} ${maybePageRange} -o sides=one-sided -d ` +
    `${printer} ${filePath}`,
      (error, stdout, stderr) => {
        exec(`rm ${filePath}`, () => { });
        if (error || stderr) {
          if(error) {
            logger.error('exec returned error:', error);
          } else {
            logger.error('exec returned stderr:', stderr);
          }
          return resolve(false);
        }
        return resolve(true);
      });
  });
}

/**
 * Download PDF file from URL.
 * @param {Sring} url : PDF file url
 * @returns Promise return the path to downloaded PDF file
 * if it was successfully download. It then returns false if there
 * was an error.
 */
async function downloadFileFromURL(url) {
  return new Promise( ( resolve ) => {
    axios({
      url: url,
      method: 'GET',
      responseType: 'stream'
    })
      .then(response => {
        // discord attachment URLs look like below, where id and name
        // are unique to the uploaded attachment
        // https://cdn.discordapp.com/attachments/<server>/<id>/<name>
        const attachmentId = url.split('/')[5];
        const fileName = `/tmp/${attachmentId}.pdf`;
        const filePath = `/tmp/${fileName}.pdf`;
        fs.writeFileSync(filePath, '');
        const fileStream = fs.createWriteStream(filePath);
        response.data.pipe(fileStream);
        logger.info('Successfully downloaded file from url to', filePath);
        resolve(filePath);
      })
      .catch(error => {
        logger.error('Unable to download file from URL:', error);
        resolve(false);
      });
  });
}

function determinePrinterForJob() {
  if (PRINTING.LEFT.ENABLED && PRINTING.RIGHT.ENABLED) {
    const randomNumber = Math.random();
    if (randomNumber < 0.5) {
      return PRINTING.LEFT.NAME;
    }
    else {
      return PRINTING.RIGHT.NAME;
    }
  } else if (PRINTING.LEFT.ENABLED) {
    logger.info('Choosing left printer because right is disabled');
    return PRINTING.LEFT.NAME;
  } else if (PRINTING.RIGHT.ENABLED) {
    logger.info('Choosing right printer because left is disabled');
    return PRINTING.RIGHT.NAME;
  }
  logger.error('No printer enabled');
}

module.exports = {
  sendRequestToPrinter,
  downloadFileFromURL,
  determinePrinterForJob
};
