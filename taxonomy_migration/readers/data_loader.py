from collections import defaultdict
from typing import Dict, List

from sqlalchemy.orm import joinedload

from db.models import (
    Question,
    Disability,
    MedicalCategory,
    MarketData,
    QuestionCategoryMap,
    QuestionTravelCategoryMap
)
from db.orm import Session


class TaxonomyDataLoader:

    def __init__(self):
        self._question_key_entity_map: Dict[str, Question] = {}
        self._disability_key_entity_map: Dict[str, Disability] = {}
        self._medical_category_key_entity_map: Dict[str, MedicalCategory] = {}
        self._travel_category_key_entity_map: Dict[str, MedicalCategory] = {}
        self._disability_key_market_data_map: Dict[str, MarketData] = {}

        self._question_key_medical_categories_map = defaultdict(Dict)
        self._question_key_travel_categories_map = defaultdict(Dict)

    def load(self):
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
                self._question_key_medical_categories_map[question_key][medical_category_key] = medical_category_map

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
                self._question_key_travel_categories_map[question_key]['']

            print(medical_category_maps)


if __name__ == '__main__':
    TaxonomyDataLoader().load()

