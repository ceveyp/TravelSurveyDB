import json
from typing import Dict

import boto3
from botocore.exceptions import ClientError


class SecretsManager:

    def __init__(self, secret_name: str):
        self._secret_name = secret_name
        session = boto3.session.Session()
        self._client = session.client(
            service_name="secretsmanager",
            region_name="us-east-1"
        )

    def get_secrets(self) -> Dict[str, str]:
        try:
            response = self._client.get_secret_value(SecretId=self._secret_name)
            return json.loads(response["SecretString"])
        except ClientError as e:
            raise e
