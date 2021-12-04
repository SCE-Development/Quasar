import {ACCESS_ID, SECRET_KEY, ACCOUNT_ID, PRINTING_QUEUE_NAME, PRINTING_BUCKET_NAME} from "../config/config.json";
// Load the AWS SDK for Node.js
const AWS = require('aws-sdk');
// Other imports
const express = require('express');
const app = express();
const fs = require('fs');
const s3 = new AWS.S3({ apiVersion: '2012-11-05' });
// AWS credentials
var creds = new AWS.Credentials(ACCESS_ID, SECRET_KEY);

// AWS config for location and passing in the credentials
AWS.config.update({
  region: 'us-west-1',
  endpoint: "https://s3.amazonaws.com",
  credentials: creds
});

console.log('grrr');

// create SQS object with api version
const sqs = new AWS.SQS({ apiVersion: '2012-11-05' });

// this is for the queue URL
const queueUrl = `https://sqs.us-west-2.amazonaws.com/${ACCOUNT_ID}/${PRINTING_QUEUE_NAME}`;

// Setup the receiveMessage parameters
const params = {
  QueueUrl: queueUrl,
  MaxNumberOfMessages: 1,
  VisibilityTimeout: 0,
  WaitTimeSeconds: 0
};

// set interval to poll --- 5 seconds
setInterval(() => {
  console.log('allen gang');

  // receive the message in the queue with the data
  sqs.receiveMessage(params, (err, data) => {

    if (err) {
      // throw err
      console.log(err, err.stack);

    } else {
      // if no error we might be in business

      if (!data.Messages) {
        // this is for when nothing is in the queue. it will spam this
        console.log('Nothing to process');
        return;
      }

      // data message will be here
      const orderData = JSON.parse(data.Messages[0].Body);
      console.log('Order received', orderData);

      const filePath = "./yowtf.pdf"

      const paramers = {
        Bucket: PRINTING_BUCKET_NAME,
        Key: `folder/${orderData.fileNo}.pdf`
      };
      s3.getObject(paramers, (err, data) => {
        if (err) console.error(err);
        console.log('hey ', data.Body.toString(), 'binary');
        fs.writeFileSync(filePath, data.Body, 'binary');
        console.log(`${filePath} has been created!`);
      });


      // orderData is now an object that contains order_id and date properties
      // Lookup order data from data storage Execute billing for order
      // Update data storage
      // Now we must delete the message so we don't handle it again
      const deleteParams = {
        QueueUrl: queueUrl,
        ReceiptHandle: data.Messages[0].ReceiptHandle
      };

      sqs.deleteMessage(deleteParams, (err, data) => {
        if (err) {
          console.log(err, err.stack);
        } else {
          console.log('Successfully deleted message from queue');
        }
      });
    }
  });
}, 1000);