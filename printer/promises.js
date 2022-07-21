/*
The file itself is a promise. I promise to donwload the file if the file exists in the s3 bucket. If the file doesn't file doesn't exist then the promise if rejected
If the promise is fulfilled and the file exists in the s4 bucket, we can then download the file and we can call this a successfull callback
If the file doesn't exist, we display the failure 
 */

function hat ()
{
return new Promise((resolve) => {
    try {
      s3.getObject(params, function (err, dataFromS3) {
        if (err) {
          logger.info('File does not exist');
          resolve(false);
        } else {
          logger.info('File exists');
          resolve(dataFromS3);
        }
      })
    }
}

async function downloads3FileReal(fileNo){
  //  Access bucket 
  const s3 = new AWS.S3({ apiVersion: '2012-11-05' });
  const params = {
    Bucket: PRINTING_BUCKET_NAME,
    Key: `folder/${fileNo}.pdf`,
  };
  return new Promise((resolve) => {
    try {
      s3.getObject(params, function (err, dataFromS3) {
        if (err) {
          logger.info('File does not exist');
          resolve(false);
        } else {
          logger.info('File exists');
          resolve(dataFromS3);
        }
      });
    } catch (e) {
      resolve(false);
    }
  });
}

async function temp(){
  return await downloads3FileReal(0.14602026812114755);
}

temp();

