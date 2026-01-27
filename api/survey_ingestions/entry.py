from api.survey_ingestions.ingestor import SurveyIngestor
from db.orm import Session
from utils.logger import get_logger, setup_logging

logger = get_logger(__name__)


def ingest_survey(survey_id: int, response_id: int):
    with Session() as db:
        SurveyIngestor(db).ingest(survey_id, response_id)
