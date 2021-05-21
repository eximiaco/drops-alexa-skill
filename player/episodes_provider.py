import boto3
# import json

# from utils import DecimalEncoder

from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr

class EpisodesProvider(object):

    def __init__(self):
        self.dynamodb = boto3.resource("dynamodb", region_name="sa-east-1")

    def get_latest(self):
        table = self.dynamodb.Table("TechAndBizEpisodes")

        try:
            response = table.query(
                KeyConditionExpression= Key('category').eq("techandbiz") & Key('pub').gte("2000-01-01T00:00:00Z"),
                Limit=1,
                ScanIndexForward=False
            )
        except ClientError as e:
            print(e.response["Error"]["Message"])
            return None
        else:
            if len(response['Items']) > 0:
                return response['Items'][0]
            else:
                return None

    def get_first(self):
        table = self.dynamodb.Table("TechAndBizEpisodes")

        try:
            response = table.query(
                KeyConditionExpression=Key('category').eq("techandbiz") & Key('pub').lte("2999-01-01T00:00:00Z"),
                Limit=1
            )
        except ClientError as e:
            print(e.response["Error"]["Message"])
            return None
        else:
            if len(response['Items']) > 0:
                return response['Items'][0]
            else:
                return None

    def search(self, episode_subject):
        table = self.dynamodb.Table("TechAndBizEpisodes")

        try:
            response = table.scan(
                FilterExpression=Attr("stitle").contains(episode_subject.lower())
            )
        except ClientError as e:
            print(e.response["Error"]["Message"])
            return None
        else:
            if len(response['Items']) > 0:
                return response['Items']
            else:
                return None

    def get(self, episode_pub):
        table = self.dynamodb.Table("TechAndBizEpisodes")

        try:
            response = table.query(
                KeyConditionExpression=Key('category').eq("techandbiz") & Key('pub').eq(episode_pub),
                Limit=1
            )
        except ClientError as e:
            print(e.response["Error"]["Message"])
            return None
        else:
            items = response['Items']
            if len(items) > 0:
                return items[0]
            else:
                return None

    def get_next(self, episode):
        table = self.dynamodb.Table("TechAndBizEpisodes")

        try:
            response = table.query(
                KeyConditionExpression=Key('category').eq("techandbiz") & Key('pub').gt(episode["pub"]),
                Limit=1
            )
        except ClientError as e:
            print(e.response["Error"]["Message"])
            return None
        else:
            items = response['Items']
            if len(items) > 0:
                return items[0]
            else:
                return None

    def get_previous(self, episode):
        table = self.dynamodb.Table("TechAndBizEpisodes")

        try:
            response = table.query(
                KeyConditionExpression=Key('category').eq("techandbiz") & Key('pub').lt(episode["pub"]),
                Limit=1,
                ScanIndexForward=False
            )
        except ClientError as e:
            print(e.response["Error"]["Message"])
            return None
        else:
            items = response['Items']
            if len(items) > 0:
                return items[0]
            else:
                return None
#
# player = EpisodesProvider()
# episode = player.get_latest()
# print(json.dumps(episode,cls=DecimalEncoder))
# episode = player.get_previous(episode)
# episode = player.get_first()
# episode = player.get_next(episode)
# episode = player.get_next(episode)
# print(episode["title"])
