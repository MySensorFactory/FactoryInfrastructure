from cicd_tools import ParameterStoreClient, SqsClient

REGION = 'eu-central-1'
ACCOUNT_ID = '781648067507'
TIMEOUT_SECONDS = 20
CICD_PARAMETER_QUEUE_URL_PARAM = "/CICD/CICDQueueUrl"

parameter_store_client = ParameterStoreClient(REGION)

sqs_queue_url = parameter_store_client.get_parameter(CICD_PARAMETER_QUEUE_URL_PARAM)

sqs_client = SqsClient(REGION, sqs_queue_url, TIMEOUT_SECONDS)

sqs_client.wait_for_event('MasterReady')
