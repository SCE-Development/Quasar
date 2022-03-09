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