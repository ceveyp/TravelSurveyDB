from pathlib import Path
from typing import Dict

from sqlmodel import SQLModel

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

    def _add_new_entities(self, spreadsheet_entities_map: Dict[str, SQLModel], db_entities_map: Dict[str, SQLModel]):
        """Add new entities from spreadsheet to DB"""
        for entity_key, entity in spreadsheet_entities_map.items():
            if entity_key in db_entities_map:
                continue
            logger.info(f"New {type(entity)} found: {entity.model_dump()}")
            self._db.add(entity)
            self._db_taxonomy.question_key_entity_map[entity_key] = entity

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

        """for question_key, taxonomy_maps in self._spreadsheet_taxonomy.question_key_taxonomy_map.items():
            for disability_key, disability_map in taxonomy_maps["disabilities"]:
                existing_question_disabilities = self._db_taxonomy.question_key_taxonomy_map[question_key][
                    "disabilities"]
                if not disability_key in existing_question_disabilities:
                    self._db.add(disability_map)"""

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
