const awsSDK = require('aws-sdk');
const { PRINTING, AWS } = require('../config/config.json');
const logger = require('./logger');


let creds = new awsSDK.Credentials(AWS.ACCESS_ID, AWS.SECRET_KEY);
awsSDK.config.update({
  region: 'us-west-2',
  endpoint: 'https://s3.amazonaws.com',
  credentials: creds
});
const s3 = new awsSDK.S3({ apiVersion: '2012-11-05' });

async function downloadFileFromS3(fileNo) {
  const s3 = new awsSDK.S3({ apiVersion: '2012-11-05' });
  const objectToDownload = {
    Bucket: PRINTING.BUCKET_NAME,
    Key: `folder/${fileNo}.pdf`,
  };
  return new Promise((resolve) => {
    try {
      s3.getObject(objectToDownload, function (err, dataFromS3) {
        if (err) {
          logger.error(`Unable to download file with id ${fileNo} :`, err);
          resolve(false);
        } else {
          logger.info(`Successfully downloaded file with id ${fileNo}`);
          resolve(dataFromS3);
        }
      });
    } catch (e) {
      logger.error('downloadFileFromS3 had an error:', e);
      resolve(false);
    }
  });
}

function deleteFileFromS3(fileNo) {
  return new Promise((resolve) => {
    const objectToDelete = {
      Bucket: PRINTING.BUCKET_NAME,
      Key: `folder/${fileNo}.pdf`,
    };
    s3.deleteObject(objectToDelete, function (err) {
      if (err) {
        logger.error('unable to delete file with name ' + fileNo);
        resolve(false);
      } else {
        logger.info('Successfully deleted file from S3 with name ' + fileNo);
        resolve(true);
      }
    });
  });
}

module.exports = {
  downloadFileFromS3,
  deleteFileFromS3,
};
