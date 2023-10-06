from cicd_tools import EventMessage, SnsClient, ParameterStoreClient

REGION = 'eu-central-1'
ACCOUNT_ID = '781648067507'
CICD_PARAMETER_TOPIC_PARAM = "/CICD/CICDTopicArn"

parameter_store_client = ParameterStoreClient(REGION)
sns_client = SnsClient(REGION)

message_data = EventMessage(event_type="MasterReady", value={})
sns_topic_arn = parameter_store_client.get_parameter(CICD_PARAMETER_TOPIC_PARAM)

response = sns_client.publish(
    topic_arn=sns_topic_arn,
    message=message_data
)

print("Master ready event published")
