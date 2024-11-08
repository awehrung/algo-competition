#!/bin/bash

# make sure this includes your registry address if you want to upload the solution
IMAGE_NAME="my-javascript-competitor:0.0.1"

docker build --no-cache -t ${IMAGE_NAME} .
docker push ${IMAGE_NAME}
