#!/bin/bash

export KUBECONFIG=/home/ubuntu/.kube/config
chmod +x functions/deployer.py
nohup python3 functions/deployer.py > deployer.log 2>&1 &
