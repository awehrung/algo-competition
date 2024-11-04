#!/bin/bash

IMAGE_NAME="my-javascript-competitor:0.0.1"

docker build --no-cache -t ${IMAGE_NAME} .
