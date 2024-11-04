#!/bin/bash

IMAGE_NAME="my-java-competitor:0.0.2"

mvn -U clean install -DskipTests
docker build --no-cache -t ${IMAGE_NAME} .
