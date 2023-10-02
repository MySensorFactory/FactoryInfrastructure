import uuid

import boto3
from pydantic import BaseModel


ONE_SECOND = 1
ONE_MINUTE = 60

class SensorData(BaseModel):
    label: str
    timestamp: int
    event_key: str


class SnsClient:
    def __init__(self):
        self.client = boto3.client('sns')

    def publish(self, message: SensorData, topic_arn: str):
        response = self.client.publish(
            TopicArn=topic_arn,
            Message=message.json(),
            MessageGroupId=str(uuid.uuid4())
        )
        return response
