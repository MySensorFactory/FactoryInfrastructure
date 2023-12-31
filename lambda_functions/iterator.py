import json
import os
import uuid

import boto3
from pydantic import BaseModel

lambda_client = boto3.client('lambda')

S3_BUCKET = os.getenv('S3_BUCKET')
ITERATOR_INPUT = os.getenv('ITERATOR_INPUT')


class IteratorData(BaseModel):
    index: int
    count: int


class IteratorInput(BaseModel):
    iterator: IteratorData


def get_input_from_s3() -> dict:
    s3_client = boto3.client('s3')
    response = s3_client.get_object(Bucket=S3_BUCKET, Key=ITERATOR_INPUT)
    file_content = response['Body'].read().decode('utf-8')
    return json.loads(file_content)


INPUT = get_input_from_s3()


def lambda_handler(event, context):
    lambda_input = IteratorInput(**event)
    index = lambda_input.iterator.index + 1
    event_key = str(uuid.uuid4())

    for execution in INPUT['executions']:
        execution['data']['event_key'] = event_key
        payload = json.dumps((execution['data'])).encode()
        lambda_client.invoke(
            FunctionName=execution['name'],
            Payload=payload,
            InvocationType='Event'
        )

    return {
        'index': index,
        'continue': index < lambda_input.iterator.count,
        'count': lambda_input.iterator.count
    }
