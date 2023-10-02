import os
import random
import time

from pydantic import BaseModel

from commons import SensorData, SnsClient

sns_client = SnsClient()
TOPIC_ARN = os.getenv('TOPIC_ARN')


class TemperatureData(BaseModel):
    temperature: float


class Temperature(SensorData):
    temperature: TemperatureData


class TemperatureInput(BaseModel):
    min_temperature: float
    max_temperature: float
    base_temperature: float
    label: str
    event_key: str


def generate_data(event, context):
    input_data = TemperatureInput(**event)

    timestamp = int(time.time())
    temperature = input_data.base_temperature + random.uniform(input_data.min_temperature,
                                                               input_data.max_temperature)

    temperature_data = TemperatureData(temperature=temperature)
    sensor_data = Temperature(temperature=temperature_data,
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
