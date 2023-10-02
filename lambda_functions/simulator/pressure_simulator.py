import os
import random
import time

from pydantic import BaseModel

from commons import SensorData, SnsClient

sns_client = SnsClient()
TOPIC_ARN = os.getenv('TOPIC_ARN')


class PressureData(BaseModel):
    pressure: float


class Pressure(SensorData):
    pressure: PressureData


class PressureInput(BaseModel):
    min_pressure_noise: float
    max_pressure_noise: float
    base_pressure: float
    label: str
    event_key: str


def generate_data(event, context):
    input_data = PressureInput(**event)

    timestamp = int(time.time())
    pressure = input_data.base_pressure + random.uniform(input_data.min_pressure_noise,
                                                         input_data.max_pressure_noise)

    pressure_data = PressureData(pressure=pressure)
    sensor_data = Pressure(pressure=pressure_data,
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
