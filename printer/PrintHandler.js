const {
  AWS
} = require('../config/config.json');
const { BUCKET_NAME, QUEUE_NAME } =  require('../config/config.json').PRINTING;
const awsSDK = require('aws-sdk');
const fs = require('fs');
const s3 = new awsSDK.S3({ apiVersion: '2012-11-05' });
const creds = new AWS.Credentials(AWS.ACCESS_ID, AWS.SECRET_KEY);
const exec = require('exec');
const { readMessageFromSqs } = require('../util/SqsMessageHandler');

awsSDK.config.update({
  region: 'us-west-1',
  endpoint: 'https://s3.amazonaws.com',
  credentials: creds,
});

const sqs = new awsSDK.SQS({ apiVersion: '2012-11-05' });

const queueUrl = `https://sqs.us-west-2.amazonaws.com/${AWS.ACCOUNT_ID}/${QUEUE_NAME}`;

const params = {
  QueueUrl: queueUrl,
  MaxNumberOfMessages: 1,
  VisibilityTimeout: 0,
  WaitTimeSeconds: 0,
};

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

  //test
  const paramers = {
    Bucket: BUCKET_NAME,
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

        sqs.deleteMessage(deleteParams, (err) => {
          if (err) throw err;
        });
      });
  });
}, 10000);
