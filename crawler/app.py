import os

import atoma
import boto3
import requests
from notifications import notify_error

dynamodb = boto3.resource("dynamodb", region_name="sa-east-1")


def get_episodes():
    response = requests.get(os.getenv("FEED_URI"))
    feed = atoma.parse_rss_bytes(response.content)
    return feed.items


def save_episodes(episodes):
    table = dynamodb.Table("TechAndBizEpisodes")

    for entry in episodes:

        title = entry.title.replace("&", "e")
        description = entry.description.replace("&", "e")

        table.update_item(
            Key={
                "category": "techandbiz",
                "pub": entry.pub_date.isoformat()
            },
            UpdateExpression="set title = :i, stitle = :s, description = :d, address = :u, ctype = :t",
            ExpressionAttributeValues={
                ':i': title,
                ':s': title.lower(),
                ':d': description,
                ':u': entry.enclosures[0].url,
                ':t': entry.enclosures[0].type,
            },
            ReturnValues="UPDATED_NEW"
        )


def lambda_handler(event, context):
    print("Obtendo feed")

    try:
        episodes = get_episodes()
        save_episodes(episodes)
    except Exception as e:
        notify_error(e)

    print("Feed obtido")
