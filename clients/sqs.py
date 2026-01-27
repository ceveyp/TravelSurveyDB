import os
import json
from typing import Dict

import boto3


# TODO: ERROR HANDLING


class SQS:
    def __init__(self):
        self._client = boto3.client("sqs")
        self._queue_url = os.environ["SQS_QUEUE_URL"]

    def send(self, payload: Dict):
        return self._client.send_message(
            QueueUrl=self._queue_url,
            MessageBody=json.dumps(payload)
        )
