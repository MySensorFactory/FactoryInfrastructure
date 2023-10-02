import os
import random
import time

from pydantic import BaseModel
from commons import SensorData, SnsClient

TOPIC_ARN = os.getenv('TOPIC_ARN')
sns_client = SnsClient()


class GasCompositionData(BaseModel):
    h2: float
    n2: float
    nh3: float
    o2: float
    co2: float


class GasComposition(SensorData):
    gas_composition: GasCompositionData


time_elapsed = 0


class GasCompositionInput(BaseModel):
    min_concentration: GasCompositionData
    max_concentration: GasCompositionData
    base_concentration: GasCompositionData
    label: str
    event_key: str


def generate_data(event, context):
    global time_elapsed
    input_data = GasCompositionInput(**event)

    timestamp = int(time.time())
    h2 = input_data.base_concentration.h2 + random.uniform(input_data.min_concentration.h2,
                                                           input_data.max_concentration.h2)
    n2 = input_data.base_concentration.n2 + random.uniform(input_data.min_concentration.n2,
                                                           input_data.max_concentration.n2)
    nh3 = input_data.base_concentration.nh3 + random.uniform(input_data.min_concentration.nh3,
                                                             input_data.max_concentration.nh3)
    o2 = input_data.base_concentration.o2 + random.uniform(input_data.min_concentration.o2,
                                                           input_data.max_concentration.o2)
    co2 = input_data.base_concentration.co2 + random.uniform(input_data.min_concentration.co2,
                                                             input_data.max_concentration.co2)

    gas_composition = GasCompositionData(h2=h2,
                                         n2=n2,
                                         nh3=nh3,
                                         o2=o2,
                                         co2=co2)
    sensor_data = GasComposition(timestamp=timestamp,
                                 gas_composition=gas_composition,
                                 label=input_data.label,
                                 event_key=input_data.event_key)

    sns_response = sns_client.publish(message=sensor_data,
                                      topic_arn=TOPIC_ARN)

    return {
        "statusCode": 200,
        "body": "Message sent. MessageId: " + sns_response['MessageId']
    }


def lambda_handler(event, context):
    return generate_data(event, context)
