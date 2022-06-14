/**
 * Reads SQS messages and returns the message if available
 * @param {Object} params Queue URL and other SQS attributes
 * @param {Object} sqs AWS SQS service object
 * @returns {Promise} Returns false if no message was received 
 * or if there was an error, otherwise returns the received message
 */
function readMessageFromSqs(params, sqs) {
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

module.exports = { readMessageFromSqs };
