const {
  ACCESS_ID,
  SECRET_KEY,
  ACCOUNT_ID,
  PRINTING_QUEUE_NAME,
  PRINTING_BUCKET_NAME,
} = require("../config/config.json");
const AWS = require("aws-sdk");
const fs = require("fs");
const s3 = new AWS.S3({ apiVersion: "2012-11-05" });
var creds = new AWS.Credentials(ACCESS_ID, SECRET_KEY);
var exec = require("exec");

AWS.config.update({
  region: "us-west-1",
  endpoint: "https://s3.amazonaws.com",
  credentials: creds,
});

const sqs = new AWS.SQS({ apiVersion: "2012-11-05" });

const queueUrl = `https://sqs.us-west-2.amazonaws.com/${ACCOUNT_ID}/${PRINTING_QUEUE_NAME}`;

const params = {
  QueueUrl: queueUrl,
  MaxNumberOfMessages: 1,
  VisibilityTimeout: 0,
  WaitTimeSeconds: 0,
};

setInterval(() => {
  sqs.receiveMessage(params, (err, data) => {
    if (err) return;
    if (!data.Messages) return;

    const orderData = JSON.parse(data.Messages[0].Body);
    const {fileNo} = orderData;
    const path = `./${fileNo}.pdf`;

    const paramers = {
      Bucket: PRINTING_BUCKET_NAME,
      Key: `folder/${fileNo}.pdf`,
    };

    s3.getObject(paramers, (err, data) => {
      if (err) console.error(err);
      fs.writeFileSync(path, data.Body, "binary");
    });

    exec(
      "sudo lp -n 1 -o sides=one-sided -d " +
        `HP-LaserJet-p2015dn-right ${path}`,
      (error, stdout, stderr) => {
        if (error) throw error;
        if (stderr) throw stderr;
        if (error) exec(`rm ${path}`, () => { });
      }
    );

    const deleteParams = {
      QueueUrl: queueUrl,
      ReceiptHandle: data.Messages[0].ReceiptHandle,
    };

    sqs.deleteMessage(deleteParams, (err, data) => {
      if (err) throw err;
    });
  });
}, 10000);
