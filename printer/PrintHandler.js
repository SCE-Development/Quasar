const logger = require('../util/logger');
const fs = require('fs');
const {
  readMessageFromSqs,
  deleteMessageFromSqs
} = require('../util/SqsMessageHandler');
const {
  downloadFileFromS3,
  deleteFileFromS3
} = require('../util/S3BucketHandler.js');
const {
  sendRequestToPrinter,
  downloadFileFromURL,
  determinePrinterForJob
} = require('../util/PrintHandler.js');

function main() {
  logger.info('starting print handler...');

  setInterval(async () => {
    try {

      const data = await readMessageFromSqs();
      if (!data) return;
      
      // Checking if there is a file URL sent to SQS from Discord.
      const fromDiscord = (data.Body.fileURL) ? true : false;
      const printer = determinePrinterForJob();
      
      const { fileNo, copies = 1, pages = ''} = JSON.parse(data.Body);
      
      let filePath = `/tmp/${fileNo}.pdf`;
      
      if (!fromDiscord) {
        const dataFromS3 = await downloadFileFromS3(fileNo);
        if (!dataFromS3) {
          logger.warn('Unable to download file, skipping it');
          return;
        }
        fs.writeFileSync(filePath, dataFromS3.Body, 'binary');
        deleteFileFromS3(fileNo);
      } else {
        const fileDownloaded = await downloadFileFromURL(data.Body.fileURL);
        if(!fileDownloaded) return;
        filePath = fileDownloaded.pdfFilePath;
      }
      await sendRequestToPrinter({copies, pages, printer, filePath});
      await deleteMessageFromSqs({ReceiptHandle: data.ReceiptHandle});
    } catch (e) {
      logger.error('print handler had error:', e);
    }
  }, 10000);
}

main();
