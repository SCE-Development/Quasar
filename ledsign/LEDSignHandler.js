const axios = require('axios');
const config = require('../config/config.json');
const AWS = require('aws-sdk');
const { LED_URL, ACCESS_ID, SECRET_KEY, ACCOUNT_ID, LED_QUEUE_NAME } = config;
const creds = new AWS.Credentials(ACCESS_ID, SECRET_KEY);
const { sqsReadHandler } = require('../util/SqsMessageHandler');

AWS.config.update({
  region: 'us-west-1',
  endpoint: 'XXXXXXXXXXXXX',
  credentials: creds,
});

const sqs = new AWS.SQS({ apiVersion: '2012-11-05' });
const queueUrl = `https://sqs.us-west-2.amazonaws.com/${ACCOUNT_ID}/${LED_QUEUE_NAME}`;

const params = {
  QueueUrl: queueUrl,
  MaxNumberOfMessages: 1,
  VisibilityTimeout: 0,
  WaitTimeSeconds: 0,
};

setInterval(async () => {
  const orderData = await sqsReadHandler(params, sqs);
  if (!orderData) {
    return;
  }

  await axios.post(LED_URL + 'api/update-sign', orderData);
  const deleteParams = {
    QueueUrl: queueUrl,
    ReceiptHandle: data.Messages[0].ReceiptHandle,
  };
  sqs.deleteMessage(deleteParams, () => { });
}, 10000);
