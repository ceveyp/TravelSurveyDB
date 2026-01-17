from enum import StrEnum


class TaxonomySpreadsheetGridNamesEnum(StrEnum):
    QUESTIONS = 'General Questions'
    TAXONOMY = 'Taxonomy'
    MARKET_DATA = 'Market Data'


TAXONOMY_SPREADSHEET_GRID_NAMES = [
    TaxonomySpreadsheetGridNamesEnum.QUESTIONS,
    TaxonomySpreadsheetGridNamesEnum.TAXONOMY,
    TaxonomySpreadsheetGridNamesEnum.MARKET_DATA
]
