from typing import Dict

from db.models import Disability, MedicalCategory, TravelCategory


class TaxonomyData:

    def __init__(
            self,
            question_key_entity_map: Dict,
            question_key_taxonomy_map: Dict,
            disability_key_entity_map: Dict[str, Disability],
            medical_category_key_entity_map: Dict[str, MedicalCategory],
            travel_category_key_entity_map: Dict[str, TravelCategory]
    ):
        self.question_key_entity_map = question_key_entity_map
        self.question_key_taxonomy_map = question_key_taxonomy_map
        self.disability_key_entity_map = disability_key_entity_map
        self.medical_category_key_entity_map = medical_category_key_entity_map
        self.travel_category_key_entity_map = travel_category_key_entity_map
