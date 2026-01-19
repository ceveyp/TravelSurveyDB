from enum import StrEnum


class TaxonomySpreadsheetGridNamesEnum(StrEnum):
    QUESTIONS = 'questions'
    TAXONOMY = 'taxonomy'
    MARKET_DATA = 'market_data'


TAXONOMY_SPREADSHEET_GRID_NAMES = [
    TaxonomySpreadsheetGridNamesEnum.QUESTIONS,
    TaxonomySpreadsheetGridNamesEnum.TAXONOMY,
    TaxonomySpreadsheetGridNamesEnum.MARKET_DATA
]
