const { logger } = require('../util/logger');
const {
  AWS,
  PRINTING
} = require('../config/config.json');
const awsSDK = require('aws-sdk');
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
  if (!data) {
    return;
  }
  const { fileNo, copies, pageRanges } = data.Body;
  const pages = pageRanges === 'NA' ? '' : '-P ' + pageRanges;
  const path = `/tmp/${fileNo}.pdf`;
 
  const dataFromS3 = await downloadFileFromS3(fileNo);
  if (!dataFromS3) {
    logger.warn('Unable to download file, skipping it');
    return;
  }
  fs.writeFileSync(path, dataFromS3.Body, 'binary');
  const printer = determinePrinterForJob();
  exec(
    `lp -n ${copies} ${pages} -o sides=one-sided -d ` +
      `HP-LaserJet-p2015dn-${printer} ${path}`,
    (error, stdout, stderr) => {
      if(error) logger.error('exec returned error:', error);
      if(stderr) logger.error('exec returned stderr:', stderr);
      exec(`rm ${path}`, () => { });
      const deleteParams = {
        QueueUrl: queueUrl,
        ReceiptHandle: data.ReceiptHandle,
      };
      deleteFile(fileNo);
      sqs.deleteMessage(deleteParams, (err) => {
        if (err) logger.error('unable to delete message from SQS', err);
      });
    });
}, 10000);
 

