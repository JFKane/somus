#!/bin/bash

CONTAINER_NAME="somus"  
IMAGE_NAME="jfkane/somus"


docker login
docker pull $IMAGE_NAME

if [ $(docker ps -a -q -f name=$CONTAINER_NAME) ]; then
    docker stop $CONTAINER_NAME

    docker rm $CONTAINER_NAME
fi

docker run -d --name $CONTAINER_NAME -p 8000:8000 -v /home/andrei/Downloads/recordings:/app/recordings $IMAGE_NAME
