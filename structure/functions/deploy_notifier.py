from pythoncommons.cicd_tools import ParameterStoreClient, SnsClient, DeploymentMessage, Deployment
import os


def main():
    CICD_PARAMETER_TOPIC_PARAM = "/CICD/CICDTopicArn"
    CONFIG_DIR = os.environ['S3_DEPLOY_CONFIG_DIR']
    REGION = 'eu-central-1'

    parameter_store_client = ParameterStoreClient(REGION)
    sns_topic_arn = parameter_store_client.get_parameter(CICD_PARAMETER_TOPIC_PARAM)

    sns_client = SnsClient(
        region=REGION,
        topic_arn=sns_topic_arn
    )

    message_data = DeploymentMessage(event_type="Deploy",
                                     value=Deployment(config_dir=CONFIG_DIR))

    response = sns_client.publish(message=message_data)

    print(response)


if __name__ == '__main__':
    main()
