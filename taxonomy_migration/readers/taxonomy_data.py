from typing import Dict


class TaxonomyData:

    def __init__(self, question_key_entity_map: Dict, question_key_taxonomy_map: Dict):
        self.question_key_entity_map = question_key_entity_map
        self.question_key_taxonomy_map = question_key_taxonomy_map
