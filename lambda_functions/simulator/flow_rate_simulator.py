import os
import random
import time

from pydantic import BaseModel

from commons import SensorData, SnsClient

sns_client = SnsClient()
TOPIC_ARN = os.getenv('TOPIC_ARN')


class FlowRate(SensorData):
    flow_rate: float


class FlowRateInput(BaseModel):
    min_flow_rate_noise: float
    max_flow_rate_noise: float
    base_flow_rate: float
    label: str
    event_key: str


def generate_data(event, context):
    input_data = FlowRateInput(**event)

    timestamp = int(time.time())
    flow_rate = input_data.base_flow_rate + \
                random.uniform(input_data.min_flow_rate_noise, input_data.max_flow_rate_noise)

    flow_rate_data = FlowRate(flow_rate=flow_rate,
                              label=input_data.label,
                              timestamp=timestamp,
                              event_key=input_data.event_key)

    sns_response = sns_client.publish(message=flow_rate_data,
                                      topic_arn=TOPIC_ARN)

    return {
        "statusCode": 200,
        "body": "Message sent. MessageId: " + sns_response['MessageId']
    }


def lambda_handler(event, context):
    return generate_data(event, context)
