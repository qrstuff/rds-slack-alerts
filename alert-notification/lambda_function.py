import boto3
import os
import json
from datetime import datetime, timezone, timedelta
from urllib.request import Request, urlopen
import dateutil.parser


def lambda_handler(event, context):
    aws_region = os.environ.get("AWS_REGION")
    channel_id = os.environ.get("CHANNEL_ID")
    db_name = os.environ.get("DB_NAME")
    max_results = os.environ.get("MAX_RESULTS")
    alarm_name = event["alarmData"]["alarmName"]
    alarm_link = "https://{0}.console.aws.amazon.com/cloudwatch/home?region={0}#alarmsV2:alarm/{1}".format(
        aws_region, alarm_name
    )
    timestamp = dateutil.parser.parse(event["time"]).strftime('%a, %d %B %Y %H:%M:%S UTC')

    if alarm_name.split("-")[0] == "Critical":
        emote = ":bangbang:"
    else:
        emote = ":exclamation:"

    rds = boto3.client("rds")
    identifier = rds.describe_db_instances(DBInstanceIdentifier=db_name)["DBInstances"][
        0
    ]["DbiResourceId"]
    pi = boto3.client("pi")
    start_time = datetime.strftime(
        (datetime.now(timezone.utc) - timedelta(minutes=5)), "%Y-%m-%d %H:%M:%S"
    )

    response = pi.describe_dimension_keys(
        ServiceType="RDS",
        Identifier=identifier,
        StartTime=start_time,
        EndTime=datetime.now(timezone.utc),
        Metric="db.load.avg",
        GroupBy={"Group": "db.sql"},
        PartitionBy={"Group": "db.wait_event"},
        MaxResults=max_results,
    )

    query_list = []

    for n in response["Keys"]:
        query_string = n["Dimensions"]["db.sql.statement"]
        load_avg = round(n["Total"], 2)
        query = {
            "type": "rich_text",
            "elements": [
                {
                    "type": "rich_text_section",
                    "elements": [
                        {
                            "type": "text",
                            "text": "Below query has a load average of "
                        },
                        {
                            "type": "text",
                            "text": "{}:".format(load_avg),
                            "style": {"bold": True},
                        }
                    ],
                },
                {
                    "type": "rich_text_preformatted",
                    "elements": [
                        {"type": "text", "text": query_string}
                    ],
                },
            ],
        }
        query_list.append(query)

    query_data = json.dumps(query_list, indent=4, default=str)

    data = {
        "channel": channel_id,
        "icon_emoji": emote,
        "blocks": [
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": "*Namespace:*\nAWS/RDS"},
                    {"type": "mrkdwn", "text": "*Metric:*\nCPU Utilization"},
                    {"type": "mrkdwn", "text": "*Alarm Name:*\n{}".format(alarm_name)},
                    {"type": "mrkdwn", "text": "*Timestamp:*\n{}".format(timestamp)},
                ],
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "View Alarm"},
                        "value": "Cloudwatch Alarm-AWS",
                        "action_id": "actionId-0",
                        "url": alarm_link,
                    }
                ],
            },
        ],
    }

    headers = {
        "Authorization": "Bearer " + str(os.environ.get("SLACK_OAUTH_TOKEN")),
        "Content-type": "application/json; charset=utf-8",
    }

    req = Request(
        "https://slack.com/api/chat.postMessage",
        headers=headers,
        data=json.dumps(data).encode("utf-8"),
        method="POST",
    )

    response = json.loads(urlopen(req).read().decode("utf-8"))
    print(response)
    message_ts = response["message"]["ts"]

    data = {"channel": channel_id, "blocks": query_data, "thread_ts": message_ts}

    req = Request(
        "https://slack.com/api/chat.postMessage",
        headers=headers,
        data=json.dumps(data).encode("utf-8"),
        method="POST",
    )
    response = json.loads(urlopen(req).read().decode("utf-8"))
    print(response)
