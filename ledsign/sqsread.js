const axios = require('axios');
const config = require('../config/config.json');
const LED_URL = config.LED_URL;

const AWS = require('aws-sdk');

creds = new AWS.Credentials(config.ACCESS_ID, config.SECRET_KEY);
AWS.config.update({
  region: "us-west-1",
  endpoint: "XXXXXXXXXXXXX",
  credentials: creds
});

const sqs = new AWS.SQS({ apiVersion: '2012-11-05' });

const accountId = config.ACCOUNT_ID;
const queueName = config.LED_QUEUE_NAME;
const queueUrl = `https://sqs.us-west-2.amazonaws.com/${accountId}/${queueName}`;
const params = {
  QueueUrl: queueUrl,
  MaxNumberOfMessages: 1,
  VisibilityTimeout: 0,
  WaitTimeSeconds: 0
};
setInterval(() => {

  sqs.receiveMessage(params, (err, data) => {

    if (err) {
      return;
    } else {
      if (!data.Messages) {
        return;
      }
      const orderData = JSON.parse(data.Messages[0].Body);
      axios.post(LED_URL + 'api/update-sign', orderData);
      const deleteParams = {
        QueueUrl: queueUrl,
        ReceiptHandle: data.Messages[0].ReceiptHandle
      };
      sqs.deleteMessage(deleteParams, (err, data) => {
      });
    }
  });
}, 10000);