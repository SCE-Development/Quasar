const express = require('express');
const axios = require('axios');
const app = express();
const http = require("http");
const hostname = 'X.X.X.X';
const port = 8083;
const LED_URL = 'XXXXXXXXXXXXX';

//Create HTTP server and listen on port 3000 for requests
const server = http.Server(app);

// send as part of request body which isn't present in url
app.use(express.json());

app.get('/healthCheck', (req, res) => {
  axios.get(LED_URL + 'api/health-check')
    .then(response => {
      res.send(response.data);
    })
    .catch(error => {
      console.error('ERROR', error);
    });
});

app.post('/updateSignText', (req, res) => {
  axios.post(LED_URL + 'api/update-sign', req.body)
    .then(response => {
      res.send(response.data);
    })
    .catch(error => {
      console.error('ERROR', error);
    });
});

//listen for request on port 8083, and as a callback function have the port listened on logged
server.listen(port, hostname, () => {
  console.log(`Server running at http://${hostname}:${port}/`);
});

const AWS = require('aws-sdk');
const config = require('../config/config.json');

creds = new AWS.Credentials(config.ACCESS_ID, config.SECRET_KEY);
AWS.config.update({
  region: "us-west-1",
  endpoint: "XXXXXXXXXXXXX",
  credentials: creds
});

const sqs = new AWS.SQS({ apiVersion: '2012-11-05' });

const accountId = config.ACCOUNT_ID;
const queueName = config.LED_QUEUE_NAME;
const queueUrl = `https://sqs.us-west-2.amazonaws.com/${accountId}/${queueName}`;
const params = {
  QueueUrl: queueUrl,
  MaxNumberOfMessages: 1,
  VisibilityTimeout: 0,
  WaitTimeSeconds: 0
};
setInterval(() => {

  sqs.receiveMessage(params, (err, data) => {

    if (err) {
      console.log(err, err.stack);
    } else {
      // console.log(data, "whaa");
      if (!data.Messages) {
        console.log('Nothing to process');
        return;
      }
      // console.log("I am going to parse", data.Messages[0].Body);
      const orderData = JSON.parse(data.Messages[0].Body);
      console.log('Order received', orderData);
      axios.post(LED_URL + 'api/update-sign', orderData);
      // orderData is now an object that contains order_id and date properties
      // Lookup order data from data storage
      // Execute billing for order
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