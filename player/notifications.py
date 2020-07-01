import boto3
import json
import os

client = boto3.client('sns')

def notify_error(error):
    topic_arn = os.getenv("NOTIFICATIONS_TOPIC_ARN")

    client.publish( 
        TargetArn=topic_arn,
        Message= "Ocorreu um erro no Player. Error: {}".format(error) 
    )
