const logger = require('../util/logger.js');
const {
  ACCESS_ID,
  SECRET_KEY,
  ACCOUNT_ID,
  PRINTING_QUEUE_NAME,
  PRINTING_BUCKET_NAME,
} = require('../config/config.json');
const AWS = require('aws-sdk');
const fs = require('fs');
const s3 = new AWS.S3({ apiVersion: '2012-11-05' });
const creds = new AWS.Credentials(ACCESS_ID, SECRET_KEY);
const exec = require('exec');
const { readMessageFromSqs } = require('../util/SqsMessageHandler');

AWS.config.update({
  region: 'us-west-1',
  endpoint: 'https://s3.amazonaws.com',
  credentials: creds,
});

const sqs = new AWS.SQS({ apiVersion: '2012-11-05' });

const queueUrl = `https://sqs.us-west-2.amazonaws.com/${ACCOUNT_ID}/${PRINTING_QUEUE_NAME}`;

const params = {
  QueueUrl: queueUrl,
  MaxNumberOfMessages: 1,
  VisibilityTimeout: 0,
  WaitTimeSeconds: 0,
};

function deleteFile(fileNo) {
  const paramers = {
    Bucket: PRINTING_BUCKET_NAME,
    Key: `folder/${fileNo}.pdf`,
  };

  s3.deleteObject(paramers, function (err) {
    if (err) {
      logger.error('unable to delete file with name ' + fileNo);
    } else {
      logger.info('Successfully deleted file from S3 with name ' + fileNo);
    }
  });

}
function determinePrinterForJob() {
  const randomNumber = Math.random();
  if (randomNumber < 0.5) {
    return 'left';
  }
  else {
    return 'right';
  }
}

setInterval(async () => {
  const data = await readMessageFromSqs(params, sqs);
  if (!data) {
    return;
  }

  const { fileNo, copies, pageRanges } = data.Body;
  const pages = pageRanges === 'NA' ? '' : '-P ' + pageRanges;
  const path = `/tmp/${fileNo}.pdf`;

  const paramers = {
    Bucket: PRINTING_BUCKET_NAME,
    Key: `folder/${fileNo}.pdf`,
  };

  s3.getObject(paramers, (err, dataFromS3) => {
    if (err) console.error(err);
    fs.writeFileSync(path, dataFromS3.Body, 'binary');
    const printer = determinePrinterForJob();
    exec(
      `lp -n ${copies} ${pages} -o sides=one-sided -d ` +
      `HP-LaserJet-p2015dn-${printer} ${path}`,
      (error, stdout, stderr) => {
        if (error) throw error;
        if (stderr) throw stderr;
        exec(`rm ${path}`, () => { });
        const deleteParams = {
          QueueUrl: queueUrl,
          ReceiptHandle: data.ReceiptHandle,
        };
        deleteFile(fileNo);
        sqs.deleteMessage(deleteParams, (err) => {
          if (err) throw err;
        });
      });
  });
}, 10000);

