const {
  AWS,
  PRINTING
} = require('../config/config.json');
const awsSDK = require('aws-sdk');
const creds = new awsSDK.Credentials(AWS.ACCESS_ID, AWS.SECRET_KEY);
const logger = require('../util/logger');

awsSDK.config.update({
  region: 'us-west-1',
  endpoint: 'https://s3.amazonaws.com',
  credentials: creds,
});

const sqs = new awsSDK.SQS({ apiVersion: '2012-11-05' });


/**
 * Reads SQS messages and returns the message if available
 * @param {Object} params Queue URL and other SQS attributes
 * @param {Object} sqs AWS SQS service object
 * @returns {Promise} Returns false if no message was received 
 * or if there was an error, otherwise returns the received message
 */
function readMessageFromSqs() {
  const queueUrl = `https://sqs.us-west-2.amazonaws.com/${AWS.ACCOUNT_ID}/${PRINTING.QUEUE_NAME}`;
  
  const params = {
    QueueUrl: queueUrl,
    MaxNumberOfMessages: 1,
    VisibilityTimeout: 0,
    WaitTimeSeconds: 0,
  };
  return new Promise((resolve) => {
    try {
      sqs.receiveMessage(params, (err, printRequestFromSqs) => {
        if (err) return resolve(false);
        else if (!printRequestFromSqs.Messages) {
          return resolve(false);
        }
        const data = {
          Body: JSON.parse(printRequestFromSqs.Messages[0].Body),
          ReceiptHandle: printRequestFromSqs.Messages[0].ReceiptHandle
        };
        return resolve(data);
      });
    } catch (error) {
      resolve(false);
    }
  });
}

function deleteMessageFromSqs(param) {
  const deleteParams = {
    QueueUrl: `https://sqs.us-west-2.amazonaws.com/${AWS.ACCOUNT_ID}/${PRINTING.QUEUE_NAME}`,
    ReceiptHandle: param.ReceiptHandle
  };
  return new Promise((resolve) => {
    sqs.deleteMessage(deleteParams, (err) => {
      if (err) logger.error('unable to delete message from SQS', err);
    });
    resolve(true);
  });
}

module.exports = { readMessageFromSqs, deleteMessageFromSqs };
