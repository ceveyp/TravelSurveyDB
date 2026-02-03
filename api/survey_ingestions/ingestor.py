from typing import Dict, List

from clients.google_maps import AddressValidator
from constants.hotel_questions import HotelMetaQuestions
from db.models import SurveyResponse, Question, Hotel, Answer
from db.orm import Session
from utils.alchemer import Alchemer
from utils.common import normalize_field
from utils.logger import get_logger

logger = get_logger(__name__)


class SurveyIngestor:

    def __init__(self, db: Session):
        self._db = db
        self._address_validator = AddressValidator()

    @staticmethod
    def _get_answer_by_question_text(question_text: str, question_key_entity_map: Dict[str, Dict]):
        question_key = normalize_field(question_text)
        if not question_key_entity_map.get(question_key):
            raise ValueError(f"Question does not exist in survey: {question_text}")
        answer_data = question_key_entity_map[question_key]
        if not answer_data.get("answer"):
            logger.warning(f"Answer field does not exist for question '{question_text}': {answer_data}")
            return None
        return answer_data["answer"]

    def _get_db_question_key_entity_map(self) -> Dict[str, Question]:
        """Map question keys to DB entities"""
        questions: List[Question] = self._db.query(Question).all()
        question_key_entity_map: Dict[str, Question] = {}
        for question in questions:
            question_key = normalize_field(question.question_text)
            question_key_entity_map[question_key] = question
        return question_key_entity_map

    def _get_hotel_address_line(self, survey_question_key_entity_map: Dict[str, Dict]) -> str:
        address = self._get_answer_by_question_text(HotelMetaQuestions.ADDRESS, survey_question_key_entity_map)
        city = self._get_answer_by_question_text(HotelMetaQuestions.CITY, survey_question_key_entity_map)
        country = self._get_answer_by_question_text(HotelMetaQuestions.COUNTRY, survey_question_key_entity_map)
        state = self._get_answer_by_question_text(HotelMetaQuestions.STATE, survey_question_key_entity_map)
        postal_code = self._get_answer_by_question_text(HotelMetaQuestions.POSTAL_CODE, survey_question_key_entity_map)
        return f"{address}, {city}, {state}, {postal_code}, {country}"

    def _get_hotel_place_id(self, address_line: str) -> str:
        return self._address_validator.validate(address_line)

    def _locate_hotel_from_survey_data(self, survey_question_key_entity_map: Dict[str, Dict]) -> Hotel:
        """Get address line from survey answers, geolocate and validate against known hotels"""
        logger.debug(f"Searching for hotel")
        address_line = self._get_hotel_address_line(survey_question_key_entity_map)
        logger.debug(f"Address line: {address_line}")
        place_id = self._get_hotel_place_id(address_line)
        logger.debug(f"Place ID fetched: {place_id}")
        hotel: Hotel | None = self._db.query(Hotel).filter(Hotel.place_id == place_id).one_or_none()
        if not hotel:
            raise RuntimeError(f"Hotel does not exist in DB: {address_line}")
        logger.debug(f"Hotel found: {hotel.model_dump()}")
        return hotel

    def _create_answers(
            self,
            hotel: Hotel,
            survey_question_key_entity_map: Dict[str, Dict],
            db_question_key_entity_map: Dict[str, Question]
    ) -> None:
        """Create answers for all questions found in DB"""
        logger.debug(f"Saving all survey answers")
        for question_key, answer_data in survey_question_key_entity_map.items():

            # Check question exists in DB
            if not question_key in db_question_key_entity_map:
                question_text = answer_data.get("question")
                logger.warning(f"A question exists in survey that does not exist in DB: {question_text}")
                continue

            question = db_question_key_entity_map[question_key]

            # Check answer exists
            if not answer_data.get("answer"):
                logger.warning(f"An answer field does not exist for question '{question.question_text}': {answer_data}")
                continue

            # Create DB answer
            answer = Answer()
            answer.raw_response = answer_data["answer"]

            # TODO: score question/answers
            answer.normalized_score = None

            answer.hotel = hotel
            answer.question = question

            # TODO: parse room types from survey data
            answer.room_type = None

            self._db.add(answer)

    def ingest(self, response_id: int):
        """Ingest survey and response into DB"""
        logger.debug(f"Ingesting survey responses into DB: {response_id}")

        # Fetch survey response from DB
        logger.debug(f"Fetching response from DB: {response_id}")
        response: SurveyResponse | None = (
            self._db.query(SurveyResponse)
            .filter(SurveyResponse.id == response_id)
            .one_or_none()
        )
        if not response:
            raise ValueError(f"Survey response ID not found: {response_id}")

        # Fetch survey and answers from Alchemer
        logger.debug(f"Fetching Alchemer survey response: {response_id}")
        alchemer = Alchemer()
        resp = alchemer.get_survey_response(response.survey_id, response.response_id)
        survey_data: Dict = resp["survey_data"]

        # Map question keys to DB entities
        db_question_key_entity_map = self._get_db_question_key_entity_map()

        # Map question keys to survey responses
        survey_question_key_entity_map: Dict[str, Dict] = {}
        for _, answer_data in survey_data.items():
            question_key = normalize_field(answer_data["question"])
            survey_question_key_entity_map[question_key] = answer_data

        # Locate hotel in Google Maps and DB
        hotel = self._locate_hotel_from_survey_data(survey_question_key_entity_map)
        response.hotel = hotel

        # Create question answers
        self._create_answers(hotel, survey_question_key_entity_map, db_question_key_entity_map)

        self._db.commit()
