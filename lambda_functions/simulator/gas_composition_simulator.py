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


class GasComposition(Jsonable):
    def to_json(self):
        return {
            "h2": self.h2,
            "n2": self.n2,
            "nh3": self.nh3,
            "o2": self.o2,
            "co2": self.co2
        }

    def __init__(self, h2: float, n2: float, nh3: float, o2: float, co2: float):
        self.h2 = h2
        self.n2 = n2
        self.nh3 = nh3
        self.o2 = o2
        self.co2 = co2


class SensorData(Jsonable):
    def to_json(self):
        return {
            "label": self.label,
            "timestamp": self.timestamp,
            "gas_composition": self.gas_composition.to_json(),
            'event_key': self.event_key
        }

    def __init__(self, timestamp: int, gas_composition: GasComposition, label: str, event_key: str):
        self.timestamp = timestamp
        self.gas_composition = gas_composition
        self.label = label
        self.event_key = event_key


time_elapsed = 0

ONE_SECOND = 1
ONE_MINUTE = 60


def generate_data(event, context):
    global time_elapsed
    label = event['label']
    event_key = event['event_key']

    timestamp = int(time.time())

    min_concentration = event['min_concentration']
    max_concentration = event['max_concentration']
    base_concentration = event['base_concentration']

    h2 = base_concentration["h2"] + random.uniform(min_concentration["h2"], max_concentration["h2"])
    n2 = base_concentration["n2"] + random.uniform(min_concentration["n2"], max_concentration["n2"])
    nh3 = base_concentration["nh3"] + random.uniform(min_concentration["nh3"], max_concentration["nh3"])
    o2 = base_concentration["o2"] + random.uniform(min_concentration["o2"], max_concentration["o2"])
    co2 = base_concentration["co2"] + random.uniform(min_concentration["co2"], max_concentration["co2"])

    gas_composition = GasComposition(h2, n2, nh3, o2, co2)
    sensor_data = SensorData(timestamp, gas_composition, label, event_key)

    sns_response = publish_to_sns(sensor_data)

    return {
        "statusCode": 200,
        "body": "Message sent. MessageId: " + sns_response['MessageId']
    }


def lambda_handler(event, context):
    return generate_data(event, context)
