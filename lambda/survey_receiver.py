import json
from base64 import b64decode

from db.models import SurveyResponse
from db.orm import Session
from utils.config import get_config
from utils.logger import get_logger, setup_logging

logger = get_logger(__name__)


def db_create_survey_response(db: Session, survey_id: int, response_id: int) -> SurveyResponse:
    response = SurveyResponse(
        survey_id=survey_id,
        response_id=response_id
    )
    db.add(response)
    db.flush()
    return response


def survey_receiver(event, context):
    try:
        setup_logging()
        logger.debug(f"Response received on webhook: {event}")

        config = get_config()

        # Authenticate Alchemer
        logger.debug(f"Checking authorization header")
        headers = event.get("headers") or {}
        auth_header = headers.get("Authorization") or headers.get("authorization")
        if not auth_header or not auth_header == config.webhook_secret:
            logger.warning("Unable to authenticate webhook request")
            return {
                "statusCode": 401,
                "body": "Unauthorized"
            }

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

        # Parse survey response data
        logger.debug("Parsing survey data")
        try:
            data = body["data"]
            survey_id = data["survey_id"]
            response_id = data["response_id"]
            logger.debug(f"Survey ID: {survey_id}")
            logger.debug(f"Response ID: {response_id}")
        except KeyError as e:
            logger.exception(e)
            logger.error("Survey request data is invalid")
            return {"statusCode": 400, "body": "Invalid JSON"}

        # Create survey response
        logger.debug("Creating survey response in DB")
        try:
            with Session() as db:
                response = db_create_survey_response(db, survey_id, response_id)
                response_id = response.id
                logger.debug(f"DB response ID: {response_id}")
                db.commit()
        except Exception as e:
            logger.exception(e)
            logger.error(f"Error creating survey response: {e}")
            return {"statusCode": 500}

        # Return result
        logger.debug(f"Survey created: {response_id}")
        return {
            'statusCode': 200,
            'body': json.dumps({"id": response_id})
        }
    except Exception as e:
        logger.exception(e)
        logger.error(f"Error creating survey response: {e}")
        return {"statusCode": 500}
