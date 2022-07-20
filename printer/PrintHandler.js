const logger = require('../util/logger.js');
const {
  ACCESS_ID,
  SECRET_KEY,
  ACCOUNT_ID,
  PRINTING_QUEUE_NAME,
  PRINTING_BUCKET_NAME,
} = require('../config/config.json');
const AWS = require('aws-sdk');
const fs = require('fs');
const s3 = new AWS.S3({ apiVersion: '2012-11-05' });
const creds = new AWS.Credentials(ACCESS_ID, SECRET_KEY);
const exec = require('exec');
const { readMessageFromSqs } = require('../util/SqsMessageHandler');

AWS.config.update({
  region: 'us-west-1',
  endpoint: 'https://s3.amazonaws.com',
  credentials: creds,
});

const sqs = new AWS.SQS({ apiVersion: '2012-11-05' });

const queueUrl = `https://sqs.us-west-2.amazonaws.com/${ACCOUNT_ID}/${PRINTING_QUEUE_NAME}`;

const params = {
  QueueUrl: queueUrl,
  MaxNumberOfMessages: 1,
  VisibilityTimeout: 0,
  WaitTimeSeconds: 0,
};

function deleteFile(fileNo) {
  const parms = {
    Bucket: PRINTING_BUCKET_NAME,
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
  const randomNumber = Math.random();
  if (randomNumber < 0.5) {
    return 'left';
  }
  else {
    return 'right';
  }
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
    Bucket: PRINTING_BUCKET_NAME,
    Key: `folder/${fileNo}.pdf`,
  };
});


async function downloads3FileReal(fileNo){
  //Access bucket 
  const s3 = new AWS.S3({ apiVersion: '2012-11-05' });
  const params = {
    Bucket: PRINTING_BUCKET_NAME,
    Key: `folder/${fileNo}.pdf`,
  };
  return new Promise((resolve) => {
    try {
      s3.getObject(params, function (err, dataFromS3) {
        if (err) {
          logger.info('File does not exist');
          resolve(false);
        } else {
          logger.info('File exists');
          resolve(dataFromS3);
        }
      })
    } catch (e) {
      resolve(false);
    }
  });
}

async function temp(){
  //downloads3File(0.14602026812114755);
  return await downloads3FileReal(0.14602026812114755);
}

temp();
