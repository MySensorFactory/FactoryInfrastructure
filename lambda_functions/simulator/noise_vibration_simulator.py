import json
import math
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


class VibrationData(Jsonable):
    def to_json(self):
        return {
            "amplitude": self.amplitude,
            "frequency": self.frequency
        }

    def __init__(self, amplitude: float, frequency: float):
        self.amplitude = amplitude
        self.frequency = frequency


class NoiseData(Jsonable):
    def to_json(self):
        return {
            "level": self.level
        }

    def __init__(self, level: float):
        self.level = level


class SensorData(Jsonable):
    def to_json(self):
        return {
            "label": self.label,
            "timestamp": self.timestamp,
            "noise": self.noise.to_json(),
            "vibration": self.vibration.to_json(),
            'event_key': self.event_key
        }

    def __init__(self, timestamp: int,
                 vibration: VibrationData,
                 noise: NoiseData,
                 label: str,
                 event_key: str):
        self.timestamp = timestamp
        self.vibration = vibration
        self.noise = noise
        self.label = label
        self.event_key = event_key


time_elapsed = 0

ONE_SECOND = 1
ONE_MINUTE = 60


def generate_data(event, context):
    global time_elapsed
    min_amplitude = float(event['min_amplitude'])
    max_amplitude = float(event['max_amplitude'])
    noise_level_min = int(event['noise_level_min'])
    noise_level_max = int(event['noise_level_max'])
    base_vibration_level = int(event['base_vibration_level'])
    vibration_noise = int(event['vibration_noise'])
    base_noise = int(event['base_noise'])
    label = event['label']
    event_key = event['event_key']

    timestamp = int(time.time())
    vibration_amplitude = (min_amplitude + max_amplitude) / 2 * random.uniform(min_amplitude, max_amplitude)
    time_elapsed = (time_elapsed + ONE_SECOND) % ONE_MINUTE
    vibration_frequency = base_vibration_level + math.sin(math.pi * time_elapsed / ONE_MINUTE) + \
                          random.uniform(-1 * vibration_noise, vibration_noise)
    noise_level = base_noise + random.randint(noise_level_min, noise_level_max)

    vibration_data = VibrationData(vibration_amplitude, vibration_frequency)
    noise_data = NoiseData(noise_level)
    sensor_data = SensorData(timestamp, vibration_data, noise_data, label, event_key)

    sns_response = publish_to_sns(sensor_data)

    return {
        "statusCode": 200,
        "body": "Message sent. MessageId: " + sns_response['MessageId']
    }


def lambda_handler(event, context):
    return generate_data(event, context)
