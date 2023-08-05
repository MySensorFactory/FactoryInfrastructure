import boto3
import os

client = boto3.client('lambda')

LAMBDA_TO_INVOKE = os.getenv('LAMBDA_TO_INVOKE')


def lambda_handler(event, context):
    index = event['iterator']['index'] + 1
    client.invoke(
        FunctionName=LAMBDA_TO_INVOKE,
        InvocationType='Event'
    )
    return {
        'index': index,
        'continue': index < event['iterator']['count'],
        'count': event['iterator']['count']
    }
