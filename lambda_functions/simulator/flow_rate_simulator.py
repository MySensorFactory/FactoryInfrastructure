import json
import os
import random
import time
import uuid
from abc import abstractmethod

import boto3

sns_client = boto3.client('sns')
TOPIC_ARN = os.getenv('TOPIC_ARN')


class Jsonable:
    @abstractmethod
    def to_json(self) -> dict: pass


def publish_to_sns(message: Jsonable):
    response = sns_client.publish(
        TopicArn=TOPIC_ARN,
        Message=json.dumps(message.to_json()),
        MessageGroupId=str(uuid.uuid4())
    )
    return response


class FlowRateData(Jsonable):
    def to_json(self):
        return {
            "flow_rate": self.flow_rate
        }

    def __init__(self, flow_rate: float):
        self.flow_rate = flow_rate


class SensorData(Jsonable):
    def to_json(self):
        return {
            "label": self.label,
            "timestamp": self.timestamp,
            "flow_rate": self.flow_rate.to_json()
        }

    def __init__(self, timestamp: int, flow_rate: FlowRateData, label: str):
        self.timestamp = timestamp
        self.flow_rate = flow_rate
        self.label = label


def generate_data(event, context):
    min_flow_rate = float(event['min_flow_rate_noise'])
    max_flow_rate = float(event['max_flow_rate_noise'])
    base_flow_rate = float(event['base_flow_rate'])
    label = event['label']

    timestamp = int(time.time())
    flow_rate = base_flow_rate + random.uniform(min_flow_rate, max_flow_rate)

    flow_rate_data = FlowRateData(flow_rate)
    sensor_data = SensorData(timestamp, flow_rate_data, label)

    sns_response = publish_to_sns(sensor_data)

    return {
        "statusCode": 200,
        "body": "Message sent. MessageId: " + sns_response['MessageId']
    }


def lambda_handler(event, context):
    return generate_data(event, context)
