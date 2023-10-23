import boto3

REGION = 'eu-central-1'
BUCKET_NAME = 'factory-ci-cd'
s3_client = boto3.client('s3', region_name=REGION)
lambda_client = boto3.client('lambda', region_name=REGION)

s3_bucket = BUCKET_NAME
s3_folder = 'applications/lambda/'

zip_to_lambda_map = {
    'flow_rate_simulator.zip': 'FlowRateSimulator',
    'gas_composition_simulator.zip': 'GasCompositionSimulator',
    'noise_vibration_simulator.zip': 'NoiseVibrationSimulator',
    'pressure_simulator.zip': 'PressureSimulator',
    'temperature_simulator.zip': 'TemperatureSimulator',
    'iterator.zip': 'Iterator'
}

layers = {
    'commons.zip' : 'CommonsLambdaLayer'
}

layer_version = 1

def update_lambdas():

    for zip_file, lambda_name in zip_to_lambda_map.items():
        s3_key = s3_folder + zip_file

        response = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
        lambda_code = response['Body'].read()

        lambda_client.update_function_code(
            FunctionName=lambda_name,
            ZipFile=lambda_code
        )

def update_layers():
    for zip_file, layer_name in layers:
        s3_client.download_file(BUCKET_NAME, s3_folder + zip_file, zip_file)
        with open(zip_file, 'rb') as layer_file:
            lambda_client.publish_layer_version(
                LayerName=layer_name,
                Content={
                    'ZipFile': layer_file.read()
                }
            )

if __name__ == '__main__':
    update_lambdas()
    update_layers()
