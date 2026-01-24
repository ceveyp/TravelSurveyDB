from pathlib import Path
from typing import Dict

from sqlmodel import SQLModel

from db.models import (
    QuestionDisabilityMap,
    QuestionTravelCategoryMap,
    Question,
    QuestionCategoryMap,
    Disability,
    TravelCategory
)
from db.orm import Session
from taxonomy_migration.readers.data_loader import TaxonomyDataLoader
from taxonomy_migration.readers.spreadsheet import TaxonomySpreadsheetReader
from taxonomy_migration.readers.taxonomy_data import TaxonomyData
from utils.logger import get_logger, setup_logging

logger = get_logger(__name__)


class TaxonomyMigrator:
    def __init__(self, db: Session, file_path: str):
        setup_logging()
        self._db = db
        self._file_path = Path(file_path)
        self._reader = TaxonomySpreadsheetReader(file_path)
        self._loader = TaxonomyDataLoader(self._db)
        self._spreadsheet_taxonomy: TaxonomyData | None = None
        self._db_taxonomy: TaxonomyData | None = None
        self._new_entity_counters = {
            "questions": 0,
            "disabilities": 0,
            "travel_categories": 0,
            "medical_categories": 0,
            "question_disability_maps": 0,
            "question_travel_category_maps": 0,
            "question_medical_category_maps": 0
        }

    def _add_new_entities(self, spreadsheet_entities_map: Dict[str, SQLModel], db_entities_map: Dict[str, SQLModel]):
        """Add new entities from spreadsheet to DB"""
        for entity_key, entity in spreadsheet_entities_map.items():
            if entity_key in db_entities_map:
                continue
            logger.info(f"New {type(entity)} found: {entity.model_dump()}")
            self._db.add(entity)
            db_entities_map[entity_key] = entity
            if isinstance(entity, Disability):
                new_counter_key = 'disabilities'
            elif isinstance(entity, Question):
                new_counter_key = 'questions'
            elif isinstance(entity, TravelCategory):
                new_counter_key = 'travel_categories'
            else:
                new_counter_key = 'medical_categories'
            self._new_entity_counters[new_counter_key] += 1

    def _add_new_question_disability_maps(self, question: Question, taxonomy_maps: Dict):
        """Add new question-disability maps from spreadsheet to DB"""
        question_key = question.question_key
        question_key_taxonomy_map = self._db_taxonomy.question_key_taxonomy_map
        existing_question_disabilities = question_key_taxonomy_map[question_key]["disabilities"]
        for disability_key, disability_map in taxonomy_maps["disabilities"].items():
            if not disability_key in existing_question_disabilities:
                qdm = QuestionDisabilityMap()
                qdm.question = question
                qdm.disability = self._db_taxonomy.disability_key_entity_map[disability_key]
                qdm.reason = disability_map.reason
                self._db.add(qdm)
                self._new_entity_counters["question_disability_maps"] += 1

    def _add_new_question_travel_category_maps(self, question: Question, taxonomy_maps: Dict):
        """Add new question-travel category maps from spreadsheet to DB"""
        question_key = question.question_key
        question_key_taxonomy_map = self._db_taxonomy.question_key_taxonomy_map
        existing_question_travel_categories = question_key_taxonomy_map[question_key]["travel_categories"]
        for travel_category_key, travel_category_map in taxonomy_maps["travel_categories"].items():
            if not travel_category_key in existing_question_travel_categories:
                q_tcm = QuestionTravelCategoryMap()
                q_tcm.question = question
                q_tcm.travel_category = self._db_taxonomy.travel_category_key_entity_map[travel_category_key]
                self._db.add(q_tcm)
                self._new_entity_counters["question_travel_category_maps"] += 1

    def _add_new_question_medical_category_maps(self, question: Question, taxonomy_maps: Dict):
        """Add new question-medical category maps from spreadsheet to DB"""
        question_key = question.question_key
        question_key_taxonomy_map = self._db_taxonomy.question_key_taxonomy_map
        existing_question_medical_categories = question_key_taxonomy_map[question_key]["medical_categories"]
        for medical_category_key, medical_category_map in taxonomy_maps["medical_categories"].items():
            if not medical_category_key in existing_question_medical_categories:
                q_mcm = QuestionCategoryMap()
                q_mcm.question = question
                q_mcm.category = self._db_taxonomy.medical_category_key_entity_map[medical_category_key]
                self._db.add(q_mcm)
                self._new_entity_counters["question_medical_category_maps"] += 1

    def _display_add_new_taxonomies_output(self):
        print("--------------------------------")
        print("\nFinished adding new taxonomies:")
        print(f"\n\tAdded {self._new_entity_counters["questions"]} Questions")
        print(f"\n\tAdded {self._new_entity_counters["disabilities"]} Disabilities")
        print(f"\n\tAdded {self._new_entity_counters["travel_categories"]} Travel Categories")
        print(f"\n\tAdded {self._new_entity_counters["medical_categories"]} Medical Categories\n")

        print(f"\n\tAdded {self._new_entity_counters["question_disability_maps"]} Question > Disability maps")
        print(f"\n\tAdded {self._new_entity_counters["question_travel_category_maps"]} Question > Travel Category maps")
        print(
            f"\n\tAdded {self._new_entity_counters["question_medical_category_maps"]} Question > Medical Category maps")

    def _add_new_taxonomy(self):
        """Add new taxonomy from spreadsheet to DB"""
        logger.debug("Adding new taxonomy from spreadsheet to DB")

        st = self._spreadsheet_taxonomy
        dt = self._db_taxonomy

        # Add new entities from spreadsheet to DB
        self._add_new_entities(st.question_key_entity_map, dt.question_key_entity_map)
        self._add_new_entities(st.disability_key_entity_map, dt.disability_key_entity_map)
        self._add_new_entities(st.medical_category_key_entity_map, dt.medical_category_key_entity_map)
        self._add_new_entities(st.travel_category_key_entity_map, dt.travel_category_key_entity_map)

        for question_key, taxonomy_maps in st.question_key_taxonomy_map.items():
            question = dt.question_key_entity_map[question_key]

            # Add all new taxonomy mappings
            self._add_new_question_disability_maps(question, taxonomy_maps)
            self._add_new_question_travel_category_maps(question, taxonomy_maps)
            self._add_new_question_medical_category_maps(question, taxonomy_maps)

        self._display_add_new_taxonomies_output()

    def migrate(self):
        self._spreadsheet_taxonomy = self._reader.read()
        self._db_taxonomy = self._loader.load()
        self._add_new_taxonomy()


def migrate(file_path: str):
    with Session() as db:
        TaxonomyMigrator(db, file_path).migrate()
        db.commit()


if __name__ == '__main__':
    migrate(r"C:/Users/phili/Documents/Jobs/TravelDB/taxonomy_new.xlsx")
