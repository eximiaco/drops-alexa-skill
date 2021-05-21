#! /bin/bash

ALEXA_SKILL_ID=$1
BUCKET_NAME=$2
SNS_TOPIC_NAME=$3
REGION=sa-east-1

aws s3api head-bucket --bucket $BUCKET_NAME  2>/dev/null || aws s3 mb s3://$BUCKET_NAME --region $REGION

sam build --parameter-overrides "ParameterKey=AlexaSkillId,ParameterValue=$ALEXA_SKILL_ID ParameterKey=SNSTopicName,ParameterValue=$SNS_TOPIC_NAME" \
&& sam package --output-template-file packaged.yaml --s3-bucket $BUCKET_NAME \
&& sam deploy --template-file packaged.yaml \
           --stack-name techandbiz-application \
           --capabilities CAPABILITY_IAM \
           --parameter-overrides AlexaSkillId=$ALEXA_SKILL_ID SNSTopicName=$SNS_TOPIC_NAME \
           --region $REGION
