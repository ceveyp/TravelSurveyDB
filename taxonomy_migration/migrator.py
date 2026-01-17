from pathlib import Path

from taxonomy_migration.readers.spreadsheet import TaxonomySpreadsheetReader
from utils.logger import get_logger, setup_logging

logger = get_logger()


class TaxonomyMigrator:
    def __init__(self, file_path: str):
        setup_logging()
        self._file_path = Path(file_path)
        self._reader = TaxonomySpreadsheetReader(file_path)

    def migrate(self):
        self._reader.read()


def migrate(file_path: str):
    TaxonomyMigrator(file_path).migrate()


if __name__ == '__main__':
    migrate(r"C:/Users/phili/Documents/Jobs/TravelDB/taxonomy.ods")
