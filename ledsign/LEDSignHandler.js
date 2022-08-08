const axios = require('axios');
const awsSDK = require('aws-sdk');
const {LED_SIGN, AWS} = require('../config/config.json');
const creds = new AWS.Credentials(AWS.ACCESS_ID, AWS.SECRET_KEY);
const { readMessageFromSqs, deleteMessageFromSqs} = require('../util/SqsMessageHandler');
const logger = require('../util/logger');

awsSDK.config.update({
  region: 'us-west-1',
  endpoint: 'XXXXXXXXXXXXX',
  credentials: creds,
});

function main() {
  logger.info('starting led sign handler...');

  const queueUrl = `https://sqs.us-west-2.amazonaws.com/${AWS.ACCOUNT_ID}/${LED_SIGN.QUEUE_NAME}`;
  
  const params = {
    QueueUrl: queueUrl,
    MaxNumberOfMessages: 1,
    VisibilityTimeout: 0,
    WaitTimeSeconds: 0,
  };
  
  setInterval(async () => {
    try {
      const data = await readMessageFromSqs(params);
      if (!data) return;
      
      let result = null;
      if (data.Body.ledIsOff && data.Body.ledIsOff != undefined) {
        logger.info('turning sign off');
        result = await axios.get(LED_SIGN.URL + 'api/turn-off');
      } else {
        logger.info(`writing "${data.Body.text}" to sign`);
        result = await axios.post(LED_SIGN.URL + 'api/update-sign', data.Body);
      }
      logger.info('LED sign responded with code', result.status);
      
      const deleteParams = {
        QueueUrl: queueUrl,
        ReceiptHandle: data.ReceiptHandle,
      };
      deleteMessageFromSqs(deleteParams);
    } catch (e) {
      logger.error('led sign handler had error:', e);
    }
  }, 10000);
}

main();
