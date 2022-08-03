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
  const parms = {
    Bucket: PRINTING.BUCKET_NAME,
    Key: `folder/${fileNo}.pdf`,
  };

  s3.deleteObject(parms, function (err) {
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

/*
This function downloads any file within our SCE AWS S3 'printing dev' bucket. 
All that is needed is to pass the file number of file of choice within the S3 bucket
Using a promise function, the file number is passed as a param and if the file exists, the file is downloaded to the path below
If the file isn't there, using our logger functions it is returned that it was unable to download the file with the specified ID
 */
async function downloadFileFromS3(fileNo) {
  const s3 = new AWS.S3({ apiVersion: '2012-11-05' });
  const params = {
    Bucket: PRINTING_BUCKET_NAME,
    Key: `folder/${fileNo}.pdf`,
  };
  return new Promise((resolve) => {
    try {
      s3.getObject(params, function (err, dataFromS3) {
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

  const paramers = {
    Bucket: PRINTING.BUCKET_NAME,
    Key: `folder/${fileNo}.pdf`,
  };

  s3.getObject(paramers, (err, dataFromS3) => {
    if (err) console.error(err);
    fs.writeFileSync(path, dataFromS3.Body, 'binary');
    const printer = determinePrinterForJob();
    exec(
      `lp -n ${copies} ${pages} -o sides=one-sided -d ` +
      `HP-LaserJet-p2015dn-${printer} ${path}`,
      (error, stdout, stderr) => {
        if (error) throw error;
        if (stderr) throw stderr;
        exec(`rm ${path}`, () => { });
        const deleteParams = {
          QueueUrl: queueUrl,
          ReceiptHandle: data.ReceiptHandle,
        };
        deleteFile(fileNo);
        sqs.deleteMessage(deleteParams, (err) => {
          if (err) throw err;
        });
      });
    });
}, 10000);
