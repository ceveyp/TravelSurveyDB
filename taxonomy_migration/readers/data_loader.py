from collections import defaultdict
from typing import Dict, List

from sqlalchemy.orm import joinedload

from db.models import (
    Question,
    Disability,
    QuestionCategoryMap,
    QuestionTravelCategoryMap,
    QuestionDisabilityMap
)
from db.orm import Session
from taxonomy_migration.readers.taxonomy_data import TaxonomyData
from utils.logger import get_logger

logger = get_logger(__name__)


class TaxonomyDataLoader:

    def __init__(self):
        self._question_key_entity_map: Dict[str, Question] = {}
        self._question_key_taxonomy_map = defaultdict(lambda: defaultdict(dict))

    def load(self) -> TaxonomyData:
        logger.debug("Loading taxonomy data from DB")
        with Session() as db:
            questions: List[Question] = db.query(Question).all()
            for question in questions:
                self._question_key_entity_map[question.question_key] = question

            # Map question key to medical category
            medical_category_maps: List[QuestionCategoryMap] = (
                db.query(QuestionCategoryMap)
                .options(
                    joinedload(QuestionCategoryMap.question),
                    joinedload(QuestionCategoryMap.category)
                )
                .all()
            )
            for medical_category_map in medical_category_maps:
                question_key = medical_category_map.question.question_key
                medical_category_key = medical_category_map.category.key
                self._question_key_taxonomy_map[question_key]["medical_categories"][
                    medical_category_key] = medical_category_map

            # Map question key to travel category
            travel_category_maps: List[QuestionTravelCategoryMap] = (
                db.query(QuestionTravelCategoryMap)
                .options(
                    joinedload(QuestionTravelCategoryMap.question),
                    joinedload(QuestionTravelCategoryMap.travel_category)
                )
                .all()
            )
            for travel_category_map in travel_category_maps:
                question_key = travel_category_map.question.question_key
                travel_category_key = travel_category_map.travel_category.key
                self._question_key_taxonomy_map[question_key]["travel_categories"][
                    travel_category_key] = travel_category_map

            # Map question key to disability
            disability_maps: List[QuestionDisabilityMap] = (
                db.query(QuestionDisabilityMap)
                .options(
                    joinedload(QuestionDisabilityMap.question),
                    joinedload(QuestionDisabilityMap.disability)
                    .joinedload(Disability.market_data)
                )
                .all()
            )
            for disability_map in disability_maps:
                question_key = disability_map.question.question_key
                disability_key = disability_map.disability.key
                self._question_key_taxonomy_map[question_key]["disabilities"][disability_key] = disability_map
        logger.debug("Finished loading taxonomy data from DB")
        return TaxonomyData(
            question_key_entity_map=self._question_key_taxonomy_map,
            question_key_taxonomy_map=self._question_key_taxonomy_map
        )
