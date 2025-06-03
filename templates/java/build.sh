#!/bin/bash

if [ -z $IMAGE_NAME ]; then
  echo "Use the IMAGE_NAME variable to tag your container. Make sure to include your registry address if you want to upload the solution"
  echo "Example: "
  echo "  IMAGE_NAME=\"my.company.com/my-java-competitor:0.0.2\" ./build.sh"
  exit 1
fi

mvn -U clean install -DskipTests
docker build --no-cache -t ${IMAGE_NAME} .
docker push ${IMAGE_NAME}
