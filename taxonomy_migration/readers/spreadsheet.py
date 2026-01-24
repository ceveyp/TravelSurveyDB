import sys
from collections import defaultdict
from enum import StrEnum
from pathlib import Path
from typing import Dict, List, Type

import pandas as pd
from pandas import DataFrame
from pydantic import ValidationError
from sqlmodel import SQLModel

from constants.spreadsheet.column_names.market_data import MarketDataColumnNamesEnum
from constants.spreadsheet.column_names.questions import QuestionsColumnNamesEnum
from constants.spreadsheet.column_names.taxonomy import TaxonomyColumnNamesEnum
from constants.spreadsheet.taxonomy import TAXONOMY_SPREADSHEET_GRID_NAMES, TaxonomySpreadsheetGridNamesEnum
from db.models import (
    Disability,
    Question,
    MedicalCategory,
    TravelCategory,
    QuestionDisabilityMap,
    QuestionTravelCategoryMap,
    QuestionCategoryMap
)
from db.models.disability import MarketData
from db.models.question import QuestionInputValidator, ScoringRule
from taxonomy_migration.readers.taxonomy_data import TaxonomyData
from utils.common import get_field, normalize_field, clean_values
from utils.logger import get_logger

logger = get_logger()


class TaxonomySpreadsheetReader:

    def __init__(self, file_path: str):
        self._file_path = Path(file_path)
        if not self._file_path.exists():
            logger.error(f"Could not find file: {file_path}")
            sys.exit(1)
        self._dfs: DataFrame | None = None
        self._question_key_entity_map: Dict[str, Question] = {}
        self._disability_key_entity_map: Dict[str, Disability] = {}
        self._medical_category_key_entity_map: Dict[str, MedicalCategory] = {}
        self._travel_category_key_entity_map: Dict[str, MedicalCategory] = {}
        self._disability_key_market_data_map: Dict[str, MarketData] = {}
        self._question_key_taxonomy_map = defaultdict(lambda: defaultdict(dict))

    def _read_sheet(self, sheet: TaxonomySpreadsheetGridNamesEnum) -> List[Dict]:
        sheet = self._dfs[sheet]
        sheet_data = sheet.map(clean_values)
        return sheet_data.to_dict(orient="records")

    @staticmethod
    def _create_taxonomy(
            row: Dict,
            column_name: StrEnum,
            key_entity_map: Dict[str, SQLModel],
            model: Type[SQLModel]
    ) -> str:
        field_name = get_field(row, column_name)
        field_key = normalize_field(field_name)
        if not field_key:
            raise ValueError(f"Could not parse taxonomy sheet row: {row}")
        if not key_entity_map.get(field_key):
            entity = model(key=field_key, name=field_name)
            key_entity_map[field_key] = entity
        return field_key

    def _read_taxonomy_sheet(self):
        # Read taxonomy sheet
        logger.debug("Reading taxonomy sheet")
        taxonomy_sheet_rows = self._read_sheet(TaxonomySpreadsheetGridNamesEnum.TAXONOMY)

        column_names = TaxonomyColumnNamesEnum

        for i, row in enumerate(taxonomy_sheet_rows):
            try:
                # Create taxonomies for this row
                logger.debug(f"Creating taxonomies for row {i}")

                disability_key = self._create_taxonomy(
                    row=row,
                    column_name=column_names.DISABILITY,
                    key_entity_map=self._disability_key_entity_map,
                    model=Disability
                )
                medical_category_key = self._create_taxonomy(
                    row=row,
                    column_name=column_names.MEDICAL_CATEGORY,
                    key_entity_map=self._medical_category_key_entity_map,
                    model=MedicalCategory
                )
                travel_category_key = self._create_taxonomy(
                    row=row,
                    column_name=column_names.TRAVEL_CATEGORY,
                    key_entity_map=self._travel_category_key_entity_map,
                    model=TravelCategory
                )

                # Link taxonomies to question
                logger.debug(f"Linking taxonomies to question for row {i}")
                question_text = get_field(row, column_names.QUESTION_TEXT)
                question_key = normalize_field(question_text)
                question = self._question_key_entity_map.get(question_key)
                if not question:
                    raise ValueError(f"Taxonomy question does not exist in questions sheet: {question_text}")

                # Map question to disability
                question_disability_map = QuestionDisabilityMap()
                question_disability_map.question = question
                question_disability_map.disability = self._disability_key_entity_map[disability_key]
                question_disability_map.reason = get_field(row, column_names.REASON)
                self._question_key_taxonomy_map[question_key]["disabilities"][disability_key] = question_disability_map

                # Map question to travel category
                question_travel_category_map = QuestionTravelCategoryMap()
                question_travel_category_map.question = question
                question_travel_category_map.travel_category = self._travel_category_key_entity_map[travel_category_key]
                self._question_key_taxonomy_map[question_key]["travel_categories"][
                    travel_category_key] = question_travel_category_map

                # Map question to medical category
                question_medical_category_map = QuestionCategoryMap()
                question_medical_category_map.question = question
                question_medical_category_map.category = self._medical_category_key_entity_map[medical_category_key]
                self._question_key_taxonomy_map[question_key]["medical_categories"][
                    medical_category_key] = question_medical_category_map

            except Exception as e:
                logger.exception(e)
                logger.error(f"There was an error reading taxonomy sheet, row {i}: {e}")
        logger.debug(f"Finished mapping taxonomies")

    def _read_questions_sheet(self):
        # Read questions sheet
        logger.debug(f"Reading questions sheet")
        questions_sheet_rows = self._read_sheet(TaxonomySpreadsheetGridNamesEnum.QUESTIONS)

        logger.debug("Parsing questions sheet data")
        for i, row in enumerate(questions_sheet_rows):
            try:
                # Get question data
                question_text = get_field(row, QuestionsColumnNamesEnum.QUESTION_TEXT, str)
                question_key = normalize_field(question_text)

                # Check fields that take discrete number of values
                question_type = normalize_field(get_field(row, QuestionsColumnNamesEnum.QUESTION_TYPE, str))
                is_range = normalize_field(get_field(row, QuestionsColumnNamesEnum.IS_RANGE, str))
                applies_per_room_type = normalize_field(
                    get_field(row, QuestionsColumnNamesEnum.APPLIES_PER_ROOM_TYPE, str))
                in_assessment = normalize_field(get_field(row, QuestionsColumnNamesEnum.IN_ASSESSMENT, str))
                try:
                    QuestionInputValidator(
                        question_type=question_type,
                        is_range=is_range,
                        applies_per_room_type=applies_per_room_type,
                        in_assessment=in_assessment
                    )
                except ValidationError as e:
                    raise ValueError(f"Could not validate question (row {i + 1}): {e}")

                # Create question
                question = Question(
                    question_text=question_text,
                    question_key=question_key,
                    definition=get_field(row, QuestionsColumnNamesEnum.QUESTION_DEFINITION, str),
                    notes=get_field(row, QuestionsColumnNamesEnum.NOTES, str),
                    in_assessment=in_assessment == 'yes',
                    measurement_text=get_field(row, QuestionsColumnNamesEnum.MEASUREMENT, str),
                    is_range=is_range == 'yes',
                    question_type=question_type,
                    question_type_notes=get_field(row, QuestionsColumnNamesEnum.QUESTION_TYPE_NOTES, str),
                    survey_section=get_field(row, QuestionsColumnNamesEnum.SURVEY_SECTION, str),
                    otc_code=get_field(row, QuestionsColumnNamesEnum.OTC_CODE, int),
                    otc_list_name=get_field(row, QuestionsColumnNamesEnum.OTC_LIST_NAME, str),
                    otc_category=get_field(row, QuestionsColumnNamesEnum.OTC_CATEGORY, str),
                    applies_per_room_type=applies_per_room_type == 'yes'
                )
                self._question_key_entity_map[question_key] = question
                logger.debug(f"Question parsed: {question.model_dump()}")

                # Create scoring rule
                scoring_rule = ScoringRule(
                    operator='==',
                    max_score=get_field(row, QuestionsColumnNamesEnum.MAX_SCORE, float)
                )
                question.scoring_rule = scoring_rule
            except Exception as e:
                logger.exception(e)
                logger.error(f"There was an error reading questions sheet, row {i}: {e}")

    def _read_market_data_sheet(self):
        # Read market data sheet
        logger.debug(f"Reading market data sheet")
        market_data_rows = self._read_sheet(TaxonomySpreadsheetGridNamesEnum.MARKET_DATA)

        for i, row in enumerate(market_data_rows):
            try:
                # Get disability
                disability_name = get_field(row, MarketDataColumnNamesEnum.DISABILITY)
                disability_key = normalize_field(disability_name)
                if not self._disability_key_entity_map.get(disability_key):
                    raise ValueError(
                        f"Could not find disability from market data sheet in taxonomy sheet: {disability_name}"
                    )

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
                self._disability_key_entity_map[disability_key].market_data = market_data_point

                logger.debug(f"Market data parsed: {market_data_point.model_dump()}")
            except Exception as e:
                logger.exception(e)
                logger.error(f"There was an error reading market data sheet, row {i}: {e}")
        logger.debug(f"Finished reading market data sheet")

    def read(self) -> TaxonomyData:
        # Read all sheet data
        logger.debug(f"Reading excel sheet: {self._file_path}")
        self._dfs = pd.read_excel(
            self._file_path,
            sheet_name=TAXONOMY_SPREADSHEET_GRID_NAMES
        )
        self._read_questions_sheet()
        self._read_taxonomy_sheet()
        self._read_market_data_sheet()
        return TaxonomyData(
            question_key_entity_map=self._question_key_entity_map,
            question_key_taxonomy_map=self._question_key_taxonomy_map
        )
