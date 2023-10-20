import json
import uuid
from typing import Dict

import boto3
from pydantic import BaseModel


class EventMessage(BaseModel):
    event_type: str
    value: Dict


def is_message_not_parsable(sqs_response: dict) -> bool:
    if 'Messages' not in sqs_response:
        return True

    if len(sqs_response['Messages']) <= 0:
        return True

    return False


def get_cicd_event(sqs_response: dict) -> [EventMessage, str]:
    messages_body = sqs_response['Messages'][0]['Body']
    message_body = json.loads(messages_body)
    return EventMessage(**json.loads(message_body['Message'])), sqs_response['Messages'][0]['ReceiptHandle']


class SnsClient:
    def __init__(self, region):
        self.client = boto3.client('sns', region_name=region)

    def publish(self, message: EventMessage, topic_arn: str):
        response = self.client.publish(
            TopicArn=topic_arn,
            Message=message.json(),
            MessageGroupId=str(uuid.uuid4()),
            MessageDeduplicationId=str(uuid.uuid4())
        )
        return response


class SqsClient:
    def __init__(self, region: str, queue_url: str, timeout: int):
        self.client = boto3.client('sqs', region_name=region)
        self.queue_url = queue_url
        self.timeout = timeout

    def poll_message(self) -> dict:
        return self.client.receive_message(
            QueueUrl=self.queue_url,
            AttributeNames=[
                'All'
            ],
            MaxNumberOfMessages=1,
            MessageAttributeNames=[
                'All'
            ],
            WaitTimeSeconds=self.timeout
        )

    def delete_message(self, receipt_handle: str) -> None:
        self.client.delete_message(
            QueueUrl=self.queue_url,
            ReceiptHandle=receipt_handle
        )

    def wait_for_event(self, event_name: str) -> None:
        while True:
            response = self.poll_message()

            if is_message_not_parsable(response):
                continue

            event, receipt_handle = get_cicd_event(response)

            if event.event_type == event_name:
                print(f"Received: {event_name}")
                self.delete_message(receipt_handle)
                break


class ParameterStoreClient:
    def __init__(self, region: str):
        self.client = boto3.client('ssm', region_name=region)

    def get_parameter(self, name: str) -> str:
        return self.client.get_parameter(
            Name=name,
            WithDecryption=False
        )['Parameter']['Value']
