#!/bin/bash

echo "Building docker image ..."
echo $DOCKER_PASSWORD | docker login --username $DOCKER_USERNAME --password-stdin
docker build -t ${DOCKER_USERNAME}/${PROJECT_NAME} --build-arg DIRECTORY=target --build-arg SERVICE_NAME=$PROJECT_NAME .
docker push ${DOCKER_USERNAME}/${PROJECT_NAME}