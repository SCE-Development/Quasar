const axios = require('axios');
const config = require('../config/config.json');
const AWS = require('aws-sdk');
const { LED_URL, ACCESS_ID, SECRET_KEY, ACCOUNT_ID, LED_QUEUE_NAME } = config;
const creds = new AWS.Credentials(ACCESS_ID, SECRET_KEY);
const { readMessageFromSqs } = require('../util/SqsMessageHandler');
const client = require('prom-client');
const express = require('express')

let app = express()

let register = new client.Registry();

client.collectDefaultMetrics({ register })
const timesChanged = new client.Counter({
  name: "times_changed",
  help: "Times LED Sign has been changed"
})

register.registerMetric(timesChanged);

register.setDefaultLabels ({
  app: 'led-sign'
})



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
  const data = await readMessageFromSqs(params, sqs);
  if (!data) {
    return;
  }

  await axios.post(LED_URL + 'api/update-sign', data.Body);
  const deleteParams = {
    QueueUrl: queueUrl,
    ReceiptHandle: data.ReceiptHandle,
  };
  sqs.deleteMessage(deleteParams, () => { });
}, 10000);

app.get('/metrics', async (request, response) => {
  response.setHeader('Content-Type', register.contentType);
  response.end(await register.metrics());
})

app.listen(5000, () =>{
  console.log('Started server on port 5000');
})
