#!/bin/bash

awslocal s3 mb s3://project-choco

awslocal s3api put-object --bucket projec-choco-local --key 1

echo "Startup complete"


