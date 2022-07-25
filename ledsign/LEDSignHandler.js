const axios = require('axios');
const awsSDK = require('aws-sdk');
const {LED_SIGN, AWS} = require('../config/config.json');
const creds = new AWS.Credentials(AWS.ACCESS_ID, AWS.SECRET_KEY);
const { readMessageFromSqs } = require('../util/SqsMessageHandler');

awsSDK.config.update({
  region: 'us-west-1',
  endpoint: 'XXXXXXXXXXXXX',
  credentials: creds,
});

const sqs = new awsSDK.SQS({ apiVersion: '2012-11-05' });

const queueUrl = `https://sqs.us-west-2.amazonaws.com/${AWS.ACCOUNT_ID}/${LED_SIGN.QUEUE_NAME}`;

const params = {
  QueueUrl: queueUrl,
  MaxNumberOfMessages: 1,
  VisibilityTimeout: 0,
  WaitTimeSeconds: 0,
};

setInterval(async () => {
  const data = await readMessageFromSqs(params, sqs);
  if (!data) {
    return;
  }

  if (data.Body.ledIsOff && data.Body.ledIsOff != undefined) {
    await axios.get(LED_SIGN.IP + 'api/turn-off');
  } else {
    await axios.post(LED_SIGN.IP + 'api/update-sign', data.Body);
  }
  const deleteParams = {
    QueueUrl: queueUrl,
    ReceiptHandle: data.ReceiptHandle,
  };
  sqs.deleteMessage(deleteParams, () => {});
}, 10000);
