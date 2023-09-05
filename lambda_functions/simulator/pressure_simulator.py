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
    def to_json(self): pass


def publish_to_sns(message: Jsonable):
    response = sns_client.publish(
        TopicArn=TOPIC_ARN,
        Message=json.dumps(message.to_json()),
        MessageGroupId=str(uuid.uuid4())
    )
    return response


class PressureData(Jsonable):
    def to_json(self):
        return {
            "pressure": self.pressure
        }

    def __init__(self, pressure: float):
        self.pressure = pressure


class SensorData(Jsonable):
    def to_json(self):
        return {
            "label": self.label,
            "timestamp": self.timestamp,
            "pressure": self.pressure.to_json(),
            'event_key': self.event_key
        }

    def __init__(self, timestamp: int,
                 pressure: PressureData,
                 label: str,
                 event_key: str):
        self.timestamp = timestamp
        self.pressure = pressure
        self.label = label
        self.event_key = event_key


def generate_data(event, context):
    min_pressure_noise = float(event['min_pressure_noise'])
    max_pressure_noise = float(event['max_pressure_noise'])
    base_pressure = float(event['base_pressure'])
    label = event['label']
    event_key = event['event_key']

    timestamp = int(time.time())
    pressure = base_pressure + random.uniform(min_pressure_noise, max_pressure_noise)

    pressure_data = PressureData(pressure)
    sensor_data = SensorData(timestamp, pressure_data, label, event_key)

    sns_response = publish_to_sns(sensor_data)

    return {
        "statusCode": 200,
        "body": "Message sent. MessageId: " + sns_response['MessageId']
    }


def lambda_handler(event, context):
    return generate_data(event, context)
