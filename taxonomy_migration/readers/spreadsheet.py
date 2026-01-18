import sys
from pathlib import Path
from typing import Dict, List

import pandas as pd
from pandas import DataFrame

from constants.spreadsheet.column_names.market_data import MarketDataColumnNamesEnum
from constants.spreadsheet.column_names.questions import QuestionsColumnNamesEnum
from constants.spreadsheet.taxonomy import TAXONOMY_SPREADSHEET_GRID_NAMES, TaxonomySpreadsheetGridNamesEnum
from db.models import MarketData, Disability, Question
from taxonomy_migration.common import get_field, normalize_field, clean_values
from utils.logger import get_logger

logger = get_logger()


class TaxonomySpreadsheetReader:

    def __init__(self, file_path: str):
        self._file_path = Path(file_path)
        if not self._file_path.exists():
            logger.error(f"Could not find file: {file_path}")
            sys.exit(1)
        self._dfs: DataFrame | None = None

    def _read_sheet(self, sheet: TaxonomySpreadsheetGridNamesEnum) -> List[Dict]:
        sheet = self._dfs[sheet]
        sheet_data = sheet.map(clean_values)
        return sheet_data.to_dict(orient="records")

    def _read_questions_sheet(self):
        # Read questions sheet
        logger.debug(f"Reading questions sheet")
        questions_sheet_rows = self._read_sheet(TaxonomySpreadsheetGridNamesEnum.QUESTIONS)

        for row in questions_sheet_rows:
            question_text = get_field(row, QuestionsColumnNamesEnum.QUESTION, str)
            question_key = normalize_field(question_text)
            question = Question(
                question_text=question_text,
                question_key=question_key,
                definition=get_field(row, QuestionsColumnNamesEnum.QUESTION_DEFINITION, str),
                notes=get_field(row, QuestionsColumnNamesEnum.NOTES, str),
                in_assessment=True,
                measurement_text=get_field()
            )



    def _read_market_data_sheet(self):
        # Read market data sheet
        logger.debug(f"Reading market data sheet")
        market_data_rows = self._read_sheet(TaxonomySpreadsheetGridNamesEnum.MARKET_DATA)

        disability_key_entity_map: Dict[str, Disability] = {}
        disability_key_market_data_map: Dict[str, MarketData] = {}

        for row in market_data_rows:
            # Get disability
            disability_name = get_field(row, MarketDataColumnNamesEnum.DISABILITY, str)
            disability = Disability(name=disability_name)
            disability_key = normalize_field(disability_name)
            if not disability_key:
                logger.error(f"Could not parse row: {row}")
                continue
            disability_key_entity_map[disability_key] = disability

            # Get market data
            market_data_point = MarketData(
                impacted=get_field(row, MarketDataColumnNamesEnum.IMPACTED, int),
                impacted_workforce=get_field(row, MarketDataColumnNamesEnum.IMPACTED_WORKFORCE, int),
                likelihood=get_field(row, MarketDataColumnNamesEnum.LIKELIHOOD, float),
                labor_stat=get_field(row, MarketDataColumnNamesEnum.LABOR_STAT, float),
                statistics=get_field(row, MarketDataColumnNamesEnum.STATISTICS, str),
                statistics_source=get_field(row, MarketDataColumnNamesEnum.STATISTICS_SOURCE, str),
                labor_source=get_field(row, MarketDataColumnNamesEnum.LABOR_SOURCE, str),
                definition_source=get_field(row, MarketDataColumnNamesEnum.DEFINITION_SOURCE, str),
                definition=get_field(row, MarketDataColumnNamesEnum.DEFINITION, str)
            )
            market_data_point.disability = disability
            disability_key_market_data_map[disability_key] = market_data_point
            logger.debug(f"Market data parsed: {market_data_point.model_dump()}")

    def read(self):
        # Read all sheet data
        logger.debug(f"Reading excel sheet: {self._file_path}")
        self._dfs = pd.read_excel(
            self._file_path,
            sheet_name=TAXONOMY_SPREADSHEET_GRID_NAMES
        )
        self._read_market_data_sheet()
        self._read_questions_sheet()
