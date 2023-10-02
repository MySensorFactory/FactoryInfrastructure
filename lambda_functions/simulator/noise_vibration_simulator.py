import math
import os
import random
import time

from pydantic import BaseModel

from commons import SensorData, SnsClient, ONE_SECOND, ONE_MINUTE

sns_client = SnsClient()
TOPIC_ARN = os.getenv('TOPIC_ARN')


class VibrationData(BaseModel):
    amplitude: float
    frequency: float


class NoiseData(BaseModel):
    level: float


class NoiseAndVibration(SensorData):
    vibration: VibrationData
    noise: NoiseData


class NoiseAndVibrationInput(BaseModel):
    min_amplitude: float
    max_amplitude: float
    noise_level_min: int
    noise_level_max: int
    base_vibration_level: int
    vibration_noise: int
    base_noise: int
    label: str
    event_key: str


time_elapsed = 0


def generate_data(event, context):
    global time_elapsed
    input_data = NoiseAndVibrationInput(**event)

    timestamp = int(time.time())
    vibration_amplitude = (input_data.min_amplitude + input_data.max_amplitude) \
                          / 2 * random.uniform(input_data.min_amplitude, input_data.max_amplitude)
    time_elapsed = (time_elapsed + ONE_SECOND) % ONE_MINUTE
    vibration_frequency = input_data.base_vibration_level + math.sin(math.pi * time_elapsed / ONE_MINUTE) + \
                          random.uniform(-1 * input_data.vibration_noise, input_data.vibration_noise)
    noise_level = input_data.base_noise + random.randint(input_data.noise_level_min, input_data.noise_level_max)

    vibration_data = VibrationData(amplitude=vibration_amplitude,
                                   frequency=vibration_frequency)
    noise_data = NoiseData(level=noise_level)
    sensor_data = NoiseAndVibration(vibration=vibration_data,
                                    noise=noise_data,
                                    label=input_data.label,
                                    timestamp=timestamp,
                                    event_key=input_data.event_key)

    sns_response = sns_client.publish(message=sensor_data,
                                      topic_arn=TOPIC_ARN)

    return {
        "statusCode": 200,
        "body": "Message sent. MessageId: " + sns_response['MessageId']
    }


def lambda_handler(event, context):
    return generate_data(event, context)
