#!/bin/sh

export AWS_ACCESS_KEY_ID=$(jq -r '.ACCESS_ID' config/config.json)
export AWS_SECRET_ACCESS_KEY=$(jq -r '.SECRET_KEY' config/config.json)
export AWS_DEFAULT_REGION=$(jq -r '.AWS_DEFAULT_REGION' config/config.json)

echo Starting print server...

# Run the actual code to read from SQS/S3 and send files to the printers.
nodemon printer/PrintHandler.js
