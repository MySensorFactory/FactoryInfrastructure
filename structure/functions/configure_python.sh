#!/bin/bash

sudo apt install python3 -y
sudo apt install python3-pip -y
export CODEARTIFACT_AUTH_TOKEN=`aws codeartifact get-authorization-token --domain factory --domain-owner 781648067507 --region eu-central-1 --query authorizationToken --output text`
pip3 config set global.extra-index-url https://aws:$CODEARTIFACT_AUTH_TOKEN@factory-781648067507.d.codeartifact.region.amazonaws.com/pypi/FactoryRepository/simple/
pip3 install pythoncommons