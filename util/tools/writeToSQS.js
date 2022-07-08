const logger = require('../logger.js');
const AWS = require('aws-sdk');
const fs = require('fs');
const {
  ACCOUNT_ID,
  ACCESS_ID,
  SECRET_KEY,
  PRINTING_QUEUE_NAME,
  PRINTING_BUCKET_NAME,
} = require('../../config/config.json');
let creds = new AWS.Credentials(ACCESS_ID, SECRET_KEY);
AWS.config.update({
  region: 'us-west-2',
  endpoint: 'https://s3.amazonaws.com',
  credentials: creds
});
//  upload file to s3
const s3 = new AWS.S3({ apiVersion: '2012-11-05' });
const fileNo = Math.random();
const uploadFile = (fileNo) => {
  const params = {
    Bucket: PRINTING_BUCKET_NAME,
    Key: `folder/${fileNo}.pdf`,
    Body: fs.readFileSync('./blank.pdf')
  };
  s3.upload(params, function (err) {
    if (err) {
      logger.error('Unable to upload file ' + fileNo + 'successfully');
    }
    else {
      console.log('File uploaded successfully.');

    }
  });
};

uploadFile(fileNo);

//  send queue to sqs
function sendQueue(fileNo) {
  const sqs = new AWS.SQS({ apiVersion: '2012-11-05' });
  const queueName = PRINTING_QUEUE_NAME;
  const QueueUrl = `https://sqs.us-west-2.amazonaws.com/${ACCOUNT_ID}/${queueName}`;
  const sqsParams = {
    MessageBody: JSON.stringify({
      location: QueueUrl,
      fileName: fileNo,
    }),
    QueueUrl
  };

  sqs.sendMessage(sqsParams, function (err) {
    if (err) {
      logger.error('Unable to send queue message');
    }
    else {
      console.log('Successfull queue message sent');
      console.log('URL: ', QueueUrl);
      console.log('File Number: ', fileNo);
    }

    sqsParams.QueueUrl;
  });
}

sendQueue(fileNo);
