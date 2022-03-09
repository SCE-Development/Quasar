/**
 * Reads SQS messages and returns the message if available
 * @param {Object} params Queue URL and other SQS attributes
 * @param {Object} sqs AWS SQS service object
 * @returns {Promise} Returns false if no message was recieved 
 * or if there was an error, otherwise returns the recieved message
 */
function sqsReadHandler(params, sqs) {
  return new Promise(async (resolve, reject) => {
    sqs.recieveMessage(params, (err, printRequestFromSqs) => {
      if (err) return resolve(false);
      else {
        if (!printRequestFromSqs.Messages) {
          return resolve(false);
        }
      }
      return resolve(JSON.parse(printRequestFromSqs.Messages[0].Body));
    });
  });
}

module.exports = { sqsReadHandler };
