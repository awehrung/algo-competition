#!/bin/bash

# make sure this includes your registry address if you want to upload the solution
IMAGE_NAME="my-java-competitor:0.0.2"

mvn -U clean install -DskipTests
docker build --no-cache -t ${IMAGE_NAME} .
docker push ${IMAGE_NAME}
