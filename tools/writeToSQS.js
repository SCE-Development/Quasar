const logger = require('../util/logger.js');
const awsSDK = require('aws-sdk');
const fs = require('fs');
const {
  PRINTING,
  AWS,
} = require('../config/config.json');
let creds = new awsSDK.Credentials(AWS.ACCESS_ID, AWS.SECRET_KEY);
awsSDK.config.update({
  region: 'us-west-2',
  endpoint: 'https://s3.amazonaws.com',
  credentials: creds
});
const s3 = new awsSDK.S3({ apiVersion: '2012-11-05' });


const uploadFile = (fileNo) => {
  return new Promise((resolve, reject) => {
    const params = {
      Bucket: PRINTING.BUCKET_NAME,
      Key: `folder/${fileNo}.pdf`,
      Body: fs.readFileSync(`${process.cwd()}/tools/blank.pdf`)
    };
    s3.upload(params, function (err) {
      if (err) {
        logger.info('Upload to S3 failed!', err);
        reject(err);
      } else {
        logger.info(
          'Uploaded blank PDF successfully to',
          PRINTING.BUCKET_NAME, `in folder/${fileNo}.pdf`);
        resolve(true);
      }
    });
  });
};

function sendQueue(fileNo) {
  return new Promise((resolve, reject) => {
    const sqs = new awsSDK.SQS({ apiVersion: '2012-11-05' });
    const queueName = PRINTING.QUEUE_NAME;
    const QueueUrl = `https://sqs.us-west-2.amazonaws.com/${AWS.ACCOUNT_ID}/${queueName}`;
    const sqsParams = {
      MessageBody: JSON.stringify({
        location: QueueUrl,
        fileNo,
        copies: 1,
        pageRanges: 'NA',
      }),
      QueueUrl
    };

    sqs.sendMessage(sqsParams, function (err) {
      if (err) {
        logger.error('Unable to write to SQS!', err);
        reject(err);
      } else {
        logger.info('Successfully pushed message to SQS!', sqsParams.MessageBody);
        resolve(true);
      }
    });
  });
}

async function main() {
  try {
    const fileNo = Math.random();
    await uploadFile(fileNo);
    await sendQueue(fileNo);
  } catch (error) {
    logger.error('Exiting due to error.', error);
  }
}

main();
