from collections import defaultdict
from pathlib import Path
from typing import Dict, List

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
        self._update_entity_counters = {
            "ScoringRule": 0,
            "Question": 0,
            "QuestionDisabilityMap": 0,
            "MarketData": 0
        }
        self._delete_entity_counters = {
            "Question": 0,
            "Disability": 0,
            "MedicalCategory": 0,
            "TravelCategory": 0,
            "QuestionDisabilityMap": 0,
            "QuestionTravelCategoryMap": 0,
            "QuestionCategoryMap": 0
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
        print(f"\n\tAdded {self._new_entity_counters['questions']} Questions")
        print(f"\n\tAdded {self._new_entity_counters['disabilities']} Disabilities")
        print(f"\n\tAdded {self._new_entity_counters['travel_categories']} Travel Categories")
        print(f"\n\tAdded {self._new_entity_counters['medical_categories']} Medical Categories")

        print(f"\n\tAdded {self._new_entity_counters['question_disability_maps']} Question > Disability maps")
        print(f"\n\tAdded {self._new_entity_counters['question_travel_category_maps']} Question > Travel Category maps")
        print(
            f"\n\tAdded {self._new_entity_counters['question_medical_category_maps']} Question > Medical Category maps")

    def _display_update_taxonomies_output(self):
        print("\n\n--------------------------------")
        print("\nFinished updating taxonomies:")
        for entity_type, update_count in self._update_entity_counters.items():
            print(f"\n\tUpdated {update_count} {entity_type} entities")

    def _display_delete_taxonomies_output(self):
        print("\n\n--------------------------------")
        print("\nFinished deleting taxonomies:")
        for entity_type, update_count in self._delete_entity_counters.items():
            print(f"\n\tDeleted {update_count} {entity_type} entities")

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

        self._db.commit()

    def _update_entity(self, update_attrs: List[str], spreadsheet_entity: SQLModel, db_entity: SQLModel):
        """Polymorphic method to update changes from spreadsheet entity to DB entity"""
        for update_attr in update_attrs:
            spreadsheet_attr = getattr(spreadsheet_entity, update_attr)
            db_attr = getattr(db_entity, update_attr)
            if spreadsheet_attr == db_attr:
                continue
            setattr(db_entity, update_attr, spreadsheet_attr)
            entity_type_name = type(db_entity).__name__
            logger.debug(f"Entity attribute change detected for {entity_type_name},ID {db_entity.id}: {update_attr}")
            self._update_entity_counters[entity_type_name] += 1

    def _update_taxonomy_changes(self):
        """Update taxonomy in DB with changes in spreadsheet"""
        logger.debug("Updating taxonomy from spreadsheet to DB")

        st = self._spreadsheet_taxonomy
        dt = self._db_taxonomy

        # Update question and scoring rule entities
        logger.debug("Updating question and scoring rule entities")
        question_update_attrs = [
            'definition',
            'notes',
            'question_type_notes',
            'in_assessment',
            'otc_code',
            'otc_list_name',
            'otc_category',
            'measurement_text',
            'survey_section',
            'applies_per_room_type'
        ]
        scoring_rule_update_attrs = [
            'operator',
            'threshold_min',
            'threshold_max',
            'max_score'
        ]
        for question_key, question in st.question_key_entity_map.items():
            db_question: Question = dt.question_key_entity_map[question_key]
            self._update_entity(question_update_attrs, question, db_question)
            self._update_entity(scoring_rule_update_attrs, question.scoring_rule, db_question.scoring_rule)

        # Update taxonomy mapping reasons from spreadsheet to DB
        # reason is found in QuestionDisabilityMap entity
        logger.debug(f"Updating taxonomy mappings reasons")
        question_disability_map_update_attrs = ['reason']
        for question_disability_map_key, question_disability_map in st.question_disability_maps.items():
            if not dt.question_disability_maps.get(question_disability_map_key):
                continue
            db_question_disability_map = dt.question_disability_maps[question_disability_map_key]
            self._update_entity(
                question_disability_map_update_attrs,
                question_disability_map,
                db_question_disability_map
            )

        # Update market data for all disability entries
        logger.debug("Updating market data for all disabilities")
        market_data_update_attrs = [
            'definition',
            'impacted',
            'impacted_workforce',
            'likelihood',
            'labor_stat',
            'statistics',
            'statistics_source',
            'labor_source',
            'definition_source'
        ]
        for disability_key, disability in st.disability_key_entity_map.items():
            db_disability = dt.disability_key_entity_map[disability_key]
            self._update_entity(market_data_update_attrs, disability.market_data, db_disability.market_data)

        self._db.commit()

    def _delete_entity(self, entity: SQLModel):
        logger.debug(f"Marked one entity for deletion: {entity.model_dump()}")
        self._db.delete(entity)
        entity_type = type(entity).__name__
        self._delete_entity_counters[entity_type] += 1

    def _delete_entities(self, db_entity_map: Dict, spreadsheet_entity_map: Dict):
        deleted_entities = []
        for entity_key, entity in list(db_entity_map.items()):
            if entity_key in spreadsheet_entity_map:
                continue
            self._delete_entity(entity)
            deleted_entities.append(entity_key)
        for deleted_entity in deleted_entities:
            del db_entity_map[deleted_entity]

    def _delete_taxonomy_mappings(self):
        """Delete entity mappings which don't exist in spreadsheet"""
        logger.debug("Deleting entity mappings")
        for question_key, taxonomy_maps in self._db_taxonomy.question_key_taxonomy_map.items():
            spreadsheet_taxonomy_maps = self._spreadsheet_taxonomy.question_key_taxonomy_map.get(
                question_key, defaultdict(dict)
            )

            # Delete disability maps
            for disability_key, disability_map in taxonomy_maps["disabilities"].items():
                if disability_key in spreadsheet_taxonomy_maps["disabilities"]:
                    continue
                self._delete_entity(disability_map)

            # Delete travel category maps
            for travel_category_key, travel_category_map in taxonomy_maps["travel_categories"].items():
                if travel_category_key in spreadsheet_taxonomy_maps["travel_categories"]:
                    continue
                self._delete_entity(travel_category_map)

            # Delete medical category maps
            for medical_category_key, medical_category_map in taxonomy_maps["medical_categories"].items():
                if medical_category_key in spreadsheet_taxonomy_maps["medical_categories"]:
                    continue
                self._delete_entity(medical_category_map)

    def _delete_missing_taxonomy(self):
        """Delete taxonomy from DB that no longer exists in spreadsheet"""
        logger.debug("Deleting taxonomy from DB that no longer exists in spreadsheet")

        st = self._spreadsheet_taxonomy
        dt = self._db_taxonomy

        # Delete entities which don't exist in spreadsheet
        self._delete_entities(dt.question_key_entity_map, st.question_key_entity_map)
        self._delete_entities(dt.travel_category_key_entity_map, st.travel_category_key_entity_map)
        self._delete_entities(dt.disability_key_entity_map, st.disability_key_entity_map)
        self._delete_entities(dt.medical_category_key_entity_map, st.medical_category_key_entity_map)

        # Delete entity mappings which don't exist in spreadsheet
        self._delete_taxonomy_mappings()

        logger.debug("Finished checking for deletions")
        self._db.commit()

    def migrate(self):
        self._spreadsheet_taxonomy = self._reader.read()
        self._db_taxonomy = self._loader.load()
        self._add_new_taxonomy()
        self._update_taxonomy_changes()
        self._delete_missing_taxonomy()
        self._display_add_new_taxonomies_output()
        self._display_update_taxonomies_output()
        self._display_delete_taxonomies_output()


def migrate(file_path: str):
    with Session() as db:
        TaxonomyMigrator(db, file_path).migrate()
