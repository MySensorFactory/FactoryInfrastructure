import os
import time
import uuid
import datetime
import pandas as pd
import boto3
import io
from pydantic import BaseModel
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Constants
S3_BUCKET = os.getenv('S3_BUCKET', 'sensor-data-bucket')
S3_PREFIX = os.getenv('S3_PREFIX', 'prod_data/')
METADATA_KEY = os.getenv('METADATA_KEY', 'prod_data/historical_metadata.json')
# SNS Topic ARNs
TEMPERATURE_TOPIC_ARN = os.getenv('TEMPERATURE_TOPIC_ARN', 'arn:aws:sns:eu-central-1:123456789012:temperature-topic')
PRESSURE_TOPIC_ARN = os.getenv('PRESSURE_TOPIC_ARN', 'arn:aws:sns:eu-central-1:123456789012:pressure-topic')
VIBRATION_TOPIC_ARN = os.getenv('VIBRATION_TOPIC_ARN', 'arn:aws:sns:eu-central-1:123456789012:vibration-topic')
HUMIDITY_TOPIC_ARN = os.getenv('HUMIDITY_TOPIC_ARN', 'arn:aws:sns:eu-central-1:123456789012:humidity-topic')
ONE_MINUTE = 60

# Base data models
class SensorData(BaseModel):
    label: str
    timestamp: int
    event_key: str

# Specific sensor data models
class TemperatureData(BaseModel):
    temperature: float

class PressureData(BaseModel):
    pressure: float

class VibrationData(BaseModel):
    vibration: float

class HumidityData(BaseModel):
    humidity: float

class Temperature(SensorData):
    temperature: TemperatureData

class Pressure(SensorData):
    pressure: PressureData

class Vibration(SensorData):
    vibration: VibrationData

class Humidity(SensorData):
    humidity: HumidityData

class SnsClient:
    def __init__(self):
        self.client = boto3.client('sns')

    def publish(self, message: SensorData, topic_arn: str):
        try:
            response = self.client.publish(
                TopicArn=topic_arn,
                Message=message.json(),
                MessageGroupId=str(uuid.uuid4())
            )
            return response
        except Exception as e:
            logger.error(f"Error publishing to SNS: {e}")
            return None

class S3Client:
    def __init__(self):
        self.client = boto3.client('s3')
    
    def get_json(self, bucket, key):
        try:
            response = self.client.get_object(Bucket=bucket, Key=key)
            content = response['Body'].read().decode('utf-8')
            import json
            return json.loads(content)
        except Exception as e:
            logger.error(f"Error reading JSON from S3: {e}")
            raise
    
    def get_csv_as_dataframe(self, bucket, key):
        try:
            response = self.client.get_object(Bucket=bucket, Key=key)
            content = response['Body'].read()
            return pd.read_csv(io.BytesIO(content))
        except Exception as e:
            logger.error(f"Error reading CSV from S3: {e}")
            raise

class HistoricalDataPublisher:
    def __init__(self):
        self.sns_client = SnsClient()
        self.s3_client = S3Client()
        self.metadata = self._load_metadata()
        self.dataframes = self._load_dataframes()
        # Map of sensor types to their corresponding SNS topic ARNs
        self.topic_arns = {
            "temperature": TEMPERATURE_TOPIC_ARN,
            "pressure": PRESSURE_TOPIC_ARN,
            "vibration": VIBRATION_TOPIC_ARN,
            "humidity": HUMIDITY_TOPIC_ARN
        }
        
    def _load_metadata(self):
        logger.info(f"Loading metadata from S3: {S3_BUCKET}/{METADATA_KEY}")
        return self.s3_client.get_json(S3_BUCKET, METADATA_KEY)
    
    def _load_dataframes(self):
        dataframes = {}
        for equipment_type, filename in self.metadata["files"].items():
            s3_key = f"{S3_PREFIX}{filename}"
            try:
                logger.info(f"Loading {equipment_type} data from S3: {S3_BUCKET}/{s3_key}")
                df = self.s3_client.get_csv_as_dataframe(S3_BUCKET, s3_key)
                # Convert timestamp string to pandas datetime
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                dataframes[equipment_type] = df
                logger.info(f"Loaded {len(df)} records for {equipment_type}")
            except Exception as e:
                logger.error(f"Error loading {s3_key}: {e}")
        return dataframes
    
    def _find_closest_record(self, df, target_time):
        # Convert target_time to pandas datetime
        target_time_dt = pd.to_datetime(target_time)
        
        # Find the closest timestamp
        df['time_diff'] = abs(df['timestamp'] - target_time_dt)
        closest_record = df.loc[df['time_diff'].idxmin()]
        df.drop('time_diff', axis=1, inplace=True)
        
        return closest_record
    
    def publish_data(self):
        current_time = datetime.datetime.now()
        # Round to the nearest minute
        current_time = current_time.replace(second=0, microsecond=0)
        
        logger.info(f"Publishing data for time: {current_time}")
        
        messages_published = 0
        
        # For each equipment type
        for equipment_type, df in self.dataframes.items():
            try:
                # Find closest record to current time
                record = self._find_closest_record(df, current_time)
                
                # Get Unix timestamp
                unix_timestamp = int(time.mktime(record['timestamp'].to_pydatetime().timetuple()))
                
                # Generate a unique event key for this equipment
                event_key = f"{equipment_type.lower()}-{unix_timestamp}"
                
                # For each sensor type
                for sensor_type in self.metadata["sensor_types"]:
                    if sensor_type in record and sensor_type in self.topic_arns:
                        # Create the appropriate sensor data object
                        sensor_value = float(record[sensor_type])
                        
                        if sensor_type == "temperature":
                            sensor_data = Temperature(
                                temperature=TemperatureData(temperature=sensor_value),
                                label=equipment_type.lower(),
                                timestamp=unix_timestamp,
                                event_key=event_key
                            )
                        elif sensor_type == "pressure":
                            sensor_data = Pressure(
                                pressure=PressureData(pressure=sensor_value),
                                label=equipment_type.lower(),
                                timestamp=unix_timestamp,
                                event_key=event_key
                            )
                        elif sensor_type == "vibration":
                            sensor_data = Vibration(
                                vibration=VibrationData(vibration=sensor_value),
                                label=equipment_type.lower(),
                                timestamp=unix_timestamp,
                                event_key=event_key
                            )
                        elif sensor_type == "humidity":
                            sensor_data = Humidity(
                                humidity=HumidityData(humidity=sensor_value),
                                label=equipment_type.lower(),
                                timestamp=unix_timestamp,
                                event_key=event_key
                            )
                        
                        # Publish to the appropriate SNS topic
                        topic_arn = self.topic_arns[sensor_type]
                        response = self.sns_client.publish(message=sensor_data, topic_arn=topic_arn)
                        
                        if response and 'MessageId' in response:
                            logger.info(f"Published {sensor_type} data for {equipment_type}: {sensor_value}")
                            messages_published += 1
                        else:
                            logger.warning(f"Failed to publish {sensor_type} data for {equipment_type}")
            except Exception as e:
                logger.error(f"Error processing {equipment_type}: {e}")
        
        return {
            "statusCode": 200,
            "body": f"Published {messages_published} messages."
        }

def lambda_handler(event, context):
    publisher = HistoricalDataPublisher()
    return publisher.publish_data()

if __name__ == "__main__":
    # For local testing
    response = lambda_handler({}, None)
    print(response) 