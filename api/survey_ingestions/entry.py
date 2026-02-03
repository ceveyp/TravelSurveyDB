import json
from base64 import b64decode

from api.survey_ingestions.ingestor import SurveyIngestor
from db.orm import Session
from utils.logger import get_logger, setup_logging

logger = get_logger(__name__)


def ingest_survey(event, context):
    setup_logging()
    logger.debug(f"SQS message received: {event}")
    try:
        # Parse JSON body
        logger.debug("Parsing request body")
        if "body" not in event or event["body"] is None:
            logger.error("Body is missing")
            return {"statusCode": 400, "body": "Missing body"}
        try:
            body = event["body"]
            if event.get("isBase64Encoded"):
                body = b64decode(event["body"])
                logger.debug(f"Decoded body: {body}")
            body = json.loads(body)
        except json.JSONDecodeError as e:
            logger.exception(e)
            logger.error("JSON did not parse")
            return {"statusCode": 400, "body": "Invalid JSON"}

        # Get response ID from body
        if not body.get("id"):
            raise RuntimeError(f"Could not find response ID in request")
        response_id = body["id"]

        # Ingest survey
        with Session() as db:
            SurveyIngestor(db).ingest(response_id)

    except Exception as e:
        logger.exception(e)
        logger.error(f"There was an error ingesting survey: {e}")
