import json
from flask import Flask
import boto3
from botocore.exceptions import ClientError
from apscheduler.schedulers.background import BackgroundScheduler
from trello import TrelloClient

app = Flask(__name__)

# Use this code snippet in your app.
# If you need more information about configurations
# or implementing the sample code, visit the AWS docs:
# https://aws.amazon.com/developer/language/python/

def get_secret():

    secret_name = "awsaccesskeys"
    region_name = "eu-west-2"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    # Decrypts secret using the associated KMS key.
    secret = get_secret_value_response['SecretString']
    secretdict = json.loads(secret)
    print(secretdict)

    return secretdict


def createMessage(messageDict):
    client = TrelloClient(
        api_key='633805f187136c617b80fb4f87aad9d3',
        api_secret='34ba9afa68180131bd7f4ca4c54c53a15913e44e3d739371b8db11a4a5d0632e',
        token='ATTA37cd937a1dad491d225d52aa494d5c626de445063c26ca7069c4235b00dfb8c220A960F8'
    )

    my_list = client.get_list('645a3f827f66a1a91d15312a')
    my_list.add_card(messageDict['name'], messageDict['description'])

@app.route("/message", methods=['POST'])
def consumeMessages():
    secretdict = get_secret()
    accesskey = secretdict.get('access')
    secretkey = secretdict.get('secretaccess')
    sqs = boto3.resource('sqs', region_name='eu-west-2', aws_access_key_id=accesskey, aws_secret_access_key=secretkey)
    # Get the queue
    queue = sqs.get_queue_by_name(QueueName='MediumLowPriority')
    # Process messages by printing out body and optional author name
    for message in queue.receive_messages():
        print(message.body)
        createMessage(json.loads(message.body))
        #message.delete()

if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=consumeMessages, trigger="interval", seconds=10)
    scheduler.start()
    app.run()