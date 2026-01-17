import math
import re
from enum import StrEnum
from typing import Dict, Any

import pandas as pd


def normalize_field(value: str) -> str:
    if not value:
        return ""

    value = value.lower().strip()
    value = re.sub(r'\s+', '_', value)
    value = re.sub(r'[^a-z0-9 ]', '', value)
    return value


def get_field(row: Dict, column_name: StrEnum, value_type: Any | None = None) -> Any:
    value = row[column_name]
    if isinstance(value, float) and math.isnan(value):
        return None
    if value_type:
        value = value_type(value)
    if isinstance(value, str):
        return value.strip()
    return value


def clean_values(v):
    if pd.isna(v):
        return None
    if isinstance(v, str):
        v = v.strip()
        return v if v else None
    return v
