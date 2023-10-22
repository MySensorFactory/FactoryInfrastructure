#!/bin/bash

chmod +x deployer.py
nohup nohup python3 deployer.py > deployer.log 2>&1 &
