#!/bin/bash

if [ -z $IMAGE_NAME ]; then
  echo "Use the IMAGE_NAME variable to tag your container. Make sure to include your registry address if you want to upload the solution"
  echo "Example: "
  echo "  IMAGE_NAME=\"my.company.com/my-python-competitor:0.0.1\" ./build.sh"
  exit 1
fi

docker build --no-cache -t ${IMAGE_NAME} .
docker push ${IMAGE_NAME}
