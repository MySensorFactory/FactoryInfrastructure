import boto3
import json

account_id = '781648067507'
REGION = 'eu-central-1'

client = boto3.client("stepfunctions")

step_functions = {
    'step_functions/iterator_state_machine.json' : f'arn:aws:states:${REGION}:${account_id}:stateMachine:RepeaterStepFunction'
}

def update_step_functions():
    for json_file, function_name in step_functions.items():

        with open(json_file, 'r') as file:
            new_function_code = file.read()

        client.update_state_machine(
            stateMachineArn=function_name,
            definition=json.dumps(new_function_code)
        )

if __name__ == '__main__':
    update_step_functions()