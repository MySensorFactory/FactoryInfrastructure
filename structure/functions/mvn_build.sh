#!/bin/bash

echo "Building ..."
mvn -s settings.xml clean package -P ${BUILD_TYPE}