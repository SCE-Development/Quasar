const { logger } = require('../util/logger');
const {
  AWS,
  PRINTING
} = require('../config/config.json');
const awsSDK = require('aws-sdk');
const axios = require('axios');
const fs = require('fs');
const s3 = new awsSDK.S3({ apiVersion: '2012-11-05' });
const creds = new awsSDK.Credentials(AWS.ACCESS_ID, AWS.SECRET_KEY);
const exec = require('exec');
const { readMessageFromSqs } = require('../util/SqsMessageHandler');

awsSDK.config.update({
  region: 'us-west-1',
  endpoint: 'https://s3.amazonaws.com',
  credentials: creds,
});

const sqs = new awsSDK.SQS({ apiVersion: '2012-11-05' });

const queueUrl = `https://sqs.us-west-2.amazonaws.com/${AWS.ACCOUNT_ID}/${PRINTING.QUEUE_NAME}`;

const params = {
  QueueUrl: queueUrl,
  MaxNumberOfMessages: 1,
  VisibilityTimeout: 0,
  WaitTimeSeconds: 0,
};


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

function deleteFile(fileNo) {
  const objectToDelete = {
    Bucket: PRINTING.BUCKET_NAME,
    Key: `folder/${fileNo}.pdf`,
  };

  s3.deleteObject(objectToDelete, function (err) {
    if (err) {
      logger.error('unable to delete file with name ' + fileNo);
    } else {
      logger.info('Successfully deleted file from S3 with name ' + fileNo);
    }
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

async function downloadFileFromS3(fileNo) {
  const s3 = new AWS.S3({ apiVersion: '2012-11-05' });
  const objectToDownload = {
    Bucket: PRINTING.BUCKET_NAME,
    Key: `folder/${fileNo}.pdf`,
  };
  return new Promise((resolve) => {
    try {
      s3.getObject(objectToDownload, function (err, dataFromS3) {
        if (err) {
          logger.error(`Unable to download file with id ${fileNo} :`, err);
          resolve(false);
        } else {
          logger.info(`Successfully downloaded file with id ${fileNo}`);
          resolve(dataFromS3);
        }
      });
    } catch (e) {
      logger.error('downloadFileFromS3 had an error:', e);
      resolve(false);
    }
  });
}
 
setInterval(async () => {
  const data = await readMessageFromSqs(params, sqs);
  if (!data) return;

  // Checking if there is a file URL sent to SQS from Discord.
  const fromDiscord = (data.Body.fileURL) ? true : false;
  const printer = determinePrinterForJob();

  const { fileNo, copies = 1, pages = 'NA'} = data.Body;
  
  let filePath = `/tmp/${fileNo}.pdf`;
 
  if(!fromDiscord) {
    const dataFromS3 = await downloadFileFromS3(fileNo);
    if (!dataFromS3) {
      logger.warn('Unable to download file, skipping it');
      return;
    }
    fs.writeFileSync(filePath, dataFromS3.Body, 'binary');
    // delete file from S3
    deleteFile(fileNo);
  } else {
    const fileDownloaded = await downloadFileFromURL(data.Body.fileURL);
    if(!fileDownloaded) return;
    filePath = fileDownloaded.pdfFilePath;
  }
  exec(
    `lp -n ${copies} ${pages} -o sides=one-sided -d ` +
    `HP-LaserJet-p2015dn-${printer} ${filePath}`,
    (error, stdout, stderr) => {
      if (error) throw error;
      if (stderr) throw stderr;
      exec(`rm ${filePath}`, () => { });

      // delete from sqs
      const deleteParams = {
        QueueUrl: queueUrl,
        ReceiptHandle: data.ReceiptHandle,
      };
      sqs.deleteMessage(deleteParams, (err) => {
        if (err) logger.error('unable to delete message from SQS', err);
      });
    });
}, 10000);
 