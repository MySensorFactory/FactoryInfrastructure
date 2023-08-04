import json
import uuid

import boto3

sns_client = boto3.client('sns')
TOPIC_ARN = 'arn:aws:sns:us-east-1:781648067507:df-FactoryDataSNSTopic-WgcDxuqsmpna.fifo'


class Message:
    def __init__(self, sensor, value, timestamp, attributes=None):
        self.sensor = sensor
        self.value = value
        self.timestamp = timestamp
        self.attributes = attributes or {}

    def to_json(self):
        return json.dumps({
            "sensor": self.sensor,
            "value": self.value,
            "timestamp": self.timestamp,
            "attributes": self.attributes
        })

    @classmethod
    def from_json(cls, json_string):
        data = json.loads(json_string)
        return cls(data['sensor'], data['value'], data['timestamp'], data['attributes'])


def parse_data(event):
    data = event['Records'][0]['body']
    sensor = data['sensor']
    value = data['value']
    timestamp = data['timestamp']
    return sensor, timestamp, value


def create_response(response_body, status_code: int):
    return {
        "statusCode": status_code,
        "body": response_body
    }


def publish_to_sns(message):
    response = sns_client.publish(
        TopicArn=TOPIC_ARN,
        Message=message.to_json(),
        MessageGroupId=str(uuid.uuid4())
    )
    return response


def create_message(sensor: str, timestamp: str, value: any):
    message = Message(
        sensor=sensor,
        value=value,
        timestamp=timestamp,
        attributes={"unit": "Celsius", "location": "Living Room"}
    )
    return message


def lambda_handler(event, context):
    """Example json data

    >>> input_data = {
    >>>    "sensor": "Temperature",
    >>>    "value": 25.5,
    >>>    "timestamp": "2023-07-19T12:34:56Z"
    >>> }
    """
    try:
        sensor, timestamp, value = parse_data(event)
    except (KeyError, json.JSONDecodeError) as e:
        return create_response("Invalid input format: " + str(e), 400)

    message = create_message(sensor, timestamp, value)
    sns_response = publish_to_sns(message)

    return create_response("Message sent. MessageId: " + sns_response['MessageId'], 200)
