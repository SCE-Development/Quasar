const {
  ACCESS_ID,
  SECRET_KEY,
  LED_QUEUE_NAME,
  ACCOUNT_ID,
} = require('./config/config.json');
const AWS = require('aws-sdk');

const creds = new AWS.Credentials(ACCESS_ID, SECRET_KEY);

AWS.config.update({
  region: 'us-west-2',
  credentials: creds,
});

const sqs = new AWS.SQS({
  apiVersion: '2012-11-05',
});
const queueUrl =
  'https://sqs.us-west-2.amazonaws.com/' + ACCOUNT_ID + '/' + LED_QUEUE_NAME;

const sqsParams = {
  MessageBody: JSON.stringify({
    dessert: 'cookies',
    whatever: 123,
    becko: 'gamer',
    makeLedOff: true,
  }),
  QueueUrl: queueUrl,
};
sqs.sendMessage(sqsParams, function (err, data) {
  if (err) {
    console.log('didnt work!', err);
  } else {
    console.log('worked, becko is cool', data);
  }
});
