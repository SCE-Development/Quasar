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

let fileNo = 0.8279506604133355;

function downloadFile() {

    const path = `./${fileNo}.pdf`;

    const paramers = {
        Bucket: PRINTING_BUCKET_NAME,
        Key: `folder/${fileNo}.pdf`,
    };

    s3.getObject(paramers, (err, dataFromS3) => {
        if (err) console.error(err);
        fs.writeFileSync(path, dataFromS3.Body, 'binary');
    });
}
function deleteFile() {
    const paramers = {
        Bucket: PRINTING_BUCKET_NAME,
        Key: `folder/${fileNo}.pdf`,
    };

    s3.deleteObject(paramers, function (err, data) {
        if (err)
            console.log(err);
        else
            console.log("Successfully deleted.");
        console.log(data);
    });

}

deleteFile();
export default deleteFile;