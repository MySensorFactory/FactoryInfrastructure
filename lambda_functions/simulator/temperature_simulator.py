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


class TemperatureData(Jsonable):
    def to_json(self):
        return {
            "temperature": self.temperature
        }

    def __init__(self, temperature: float):
        self.temperature = temperature


class SensorData(Jsonable):
    def to_json(self):
        return {
            "label": self.label,
            "timestamp": self.timestamp,
            "temperature": self.temperature.to_json(),
            'event_key': self.event_key
        }

    def __init__(self, timestamp: int,
                 temperature: TemperatureData,
                 label: str,
                 event_key: str):
        self.timestamp = timestamp
        self.temperature = temperature
        self.label = label
        self.event_key = event_key


def generate_data(event, context):
    min_temperature = float(event['min_temperature'])
    max_temperature = float(event['max_temperature'])
    base_temperature = float(event['base_temperature'])
    label = event['label']
    event_key = event['event_key']

    timestamp = int(time.time())
    temperature = base_temperature + random.uniform(min_temperature, max_temperature)

    temperature_data = TemperatureData(temperature)
    sensor_data = SensorData(timestamp, temperature_data, label, event_key)

    sns_response = publish_to_sns(sensor_data)

    return {
        "statusCode": 200,
        "body": "Message sent. MessageId: " + sns_response['MessageId']
    }


def lambda_handler(event, context):
    return generate_data(event, context)
