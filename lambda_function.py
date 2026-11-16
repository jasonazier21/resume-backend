"""Visitor counter Lambda for the Cloud Resume Challenge.

Each invocation atomically increments a counter item in DynamoDB and
returns the new value as JSON: {"count": 123}.

Environment variable:
    TABLE_NAME  name of the DynamoDB table (partition key: id, type String)
"""
import json
import os

COUNTER_ID = "visits"
_table = None


def _get_table():
    """Create the DynamoDB table handle once and reuse it between invocations."""
    global _table
    if _table is None:
        import boto3  # imported here so unit tests run without boto3 installed

        _table = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])
    return _table


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def lambda_handler(event, context):
    try:
        result = _get_table().update_item(
            Key={"id": COUNTER_ID},
            UpdateExpression="ADD #c :inc",
            ExpressionAttributeNames={"#c": "count"},  # "count" is a reserved word
            ExpressionAttributeValues={":inc": 1},
            ReturnValues="UPDATED_NEW",
        )
        # DynamoDB returns numbers as Decimal, so convert before json.dumps
        count = int(result["Attributes"]["count"])
        return _response(200, {"count": count})
    except Exception as exc:  # log the real error, return a generic one
        print(f"Error updating counter: {exc}")
        return _response(500, {"error": "Could not update visitor count"})
