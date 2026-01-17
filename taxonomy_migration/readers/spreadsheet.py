import sys
from pathlib import Path
from typing import Dict

import pandas as pd
from pandas import DataFrame

from constants.spreadsheet.column_names.market_data import MarketDataColumnNamesEnum
from constants.spreadsheet.taxonomy import TAXONOMY_SPREADSHEET_GRID_NAMES, TaxonomySpreadsheetGridNamesEnum
from db.models import MarketData, Disability
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

    def _read_market_data_sheet(self):
        # Read market data sheet
        logger.debug(f"Reading market data sheet")
        market_data_sheet = self._dfs[TaxonomySpreadsheetGridNamesEnum.MARKET_DATA]
        market_data_sheet = market_data_sheet.map(clean_values)
        market_data_rows = market_data_sheet.to_dict(orient="records")

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
