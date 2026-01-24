from pathlib import Path

from db.models import Question
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
        self._loader = TaxonomyDataLoader()
        self._spreadsheet_taxonomy: TaxonomyData | None = None
        self._db_taxonomy: TaxonomyData | None = None

    def _add_new_taxonomy(self):
        """Add new taxonomy from spreadsheet to DB"""
        logger.debug("Adding new taxonomy from spreadsheet to DB")

        # Add new questions from spreadsheet to DB
        for question_key, question in self._spreadsheet_taxonomy.question_key_entity_map.items():
            if question_key in self._db_taxonomy.question_key_entity_map:
                continue
            logger.info(f"New question found: {question.model_dump()}")
            self._db.add(question)

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
