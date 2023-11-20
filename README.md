# Factory infrastructure

## Description

This project contains infrastructure files for platform. All these files are used to create platform and perform operations on it. 

### Lambda functions

This directory contains Python scripts which are used to simulate data that may be created by factory sensors. Each type of sensor has its own lambda function to simulating and publishing data on SNS topic.

Here is short description of lambda functions files:
* `{sensor-type}_simulator.py` - simulates data for sensor of given type
* `iterator.py` - this lambda function invokes other lambda functions with input specified in `iterator_input.json` 
* `iterator_input.json` - this file contains input for other lambda functions. 

### Step functions 

Here is short description of step functions files:
* `iterator_state_machine.json` - invokes `iterator.py` lambda function once per one minute. This is because lambda functions cannot be invoked periodically on their own.

### Structure

This directory contains definitions of platform structure and CICD tools.

#### Functions

This directory contains CICD tools which are used to deploy and startup cluster nodes.

Here is short description of the cicd functions:
* `cicd_tools.py` - this is library which is used by other scripts. It provides AWS and Kubernetes tools.
* `deploy.sh` - deploy maven artifact and build Docker image
* `deploy_notifier.py` - sends deploy event on CICD SNS topic
* `deployer.py` - this script is launched as daemon process and handles CICD events. If deployer handle CICD event then it deploys an application
* `mvn_build.sh` - builds maven artifact
* `receive_master_ready_event.py` - this script waits for master ready event in CICD SQS queue
* `run_deployer.sh` - launches `deployer.py` as daemon process
* `send_master_ready_event.py` - this Python script sends master ready event on CICD SNS topic
* `wait_for_all_nodes_ready.py` - this script waits for all nodes to be ready

#### Kubernetes

Here is short description of Kubernetes custom manifests:
* `cni.yml` - this is Flannel CNI manifest which has customized CIDR range which fits to CIDR specified in cluster VPC

#### Stack

The `stack.yml` file contains all cloud infrastructure. It contains definitions for the following resources:
* EC2 instances 
* lambda functions 
* step functions 
* VPC 
* CodeBuild projects
* CICD SQS queue
* CICD SNS topic
* Sensor SQS queues
* Sensor SNS topics
* Application load balancer
* Security group
* SSH KeyPair
* subnets
* lambda layers

### Updated functions

There is several scripts which are used to update elements of the platform:
* `update_lambda_deployments.py` - updates lambda functions deployments. Pulls lambdas from S3 and updates AWS lambdas as never version
* `update_step_functions.py` - updates running step function. It pulls newer step function definition from S3 and replaces it.
* `update_structure_files.py` - copies all files from this repository to S3 
