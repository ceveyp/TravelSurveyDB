from collections import defaultdict
from typing import Dict, List, Type

from sqlmodel import SQLModel

from db.models import (
    Question,
    Disability,
    QuestionCategoryMap,
    QuestionTravelCategoryMap,
    QuestionDisabilityMap,
    MedicalCategory,
    TravelCategory
)
from db.orm import Session
from taxonomy_migration.readers.taxonomy_data import TaxonomyData
from utils.logger import get_logger

logger = get_logger(__name__)


class TaxonomyDataLoader:

    def __init__(self, db: Session):
        self._db = db
        self._question_key_entity_map: Dict[str, Question] = {}
        self._question_key_taxonomy_map = defaultdict(lambda: defaultdict(dict))
        self._disability_key_entity_map: Dict[str, Disability] = {}
        self._medical_category_key_entity_map: Dict[str, MedicalCategory] = {}
        self._travel_category_key_entity_map: Dict[str, TravelCategory] = {}

    def _fetch_taxonomy_key_entity_map(self, entity_type: Type[SQLModel], entity_map: Dict[str, SQLModel]):
        entities = self._db.query(entity_type).all()
        for entity in entities:
            if isinstance(entity, Question):
                entity_map[entity.question_key] = entity
            else:
                entity_map[entity.key] = entity

    def load(self) -> TaxonomyData:
        logger.debug("Loading taxonomy data from DB")

        # Fetch all key-entity maps for all taxonomy types
        self._fetch_taxonomy_key_entity_map(Question, self._question_key_entity_map)
        self._fetch_taxonomy_key_entity_map(Disability, self._disability_key_entity_map)
        self._fetch_taxonomy_key_entity_map(MedicalCategory, self._medical_category_key_entity_map)
        self._fetch_taxonomy_key_entity_map(TravelCategory, self._travel_category_key_entity_map)

        tx_map = self._question_key_taxonomy_map

        # Map question key to medical category
        medical_category_maps: List[QuestionCategoryMap] = self._db.query(QuestionCategoryMap).all()
        for medical_category_map in medical_category_maps:
            question_key = medical_category_map.question.question_key
            medical_category_key = medical_category_map.category.key
            tx_map[question_key]["medical_categories"][medical_category_key] = medical_category_map

        # Map question key to travel category
        travel_category_maps: List[QuestionTravelCategoryMap] = self._db.query(QuestionTravelCategoryMap).all()
        for travel_category_map in travel_category_maps:
            question_key = travel_category_map.question.question_key
            travel_category_key = travel_category_map.travel_category.key
            tx_map[question_key]["travel_categories"][travel_category_key] = travel_category_map

        # Map question key to disability
        disability_maps: List[QuestionDisabilityMap] = self._db.query(QuestionDisabilityMap).all()
        for disability_map in disability_maps:
            question_key = disability_map.question.question_key
            disability_key = disability_map.disability.key
            tx_map[question_key]["disabilities"][disability_key] = disability_map

        logger.debug("Finished loading taxonomy data from DB")
        return TaxonomyData(
            question_key_entity_map=self._question_key_entity_map,
            question_key_taxonomy_map=self._question_key_taxonomy_map,
            disability_key_entity_map=self._disability_key_entity_map,
            medical_category_key_entity_map=self._medical_category_key_entity_map,
            travel_category_key_entity_map=self._travel_category_key_entity_map
        )
