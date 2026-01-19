from enum import Enum
from typing import Literal

QuestionDataTypes = Literal['boolean', 'number', 'float', 'text']


class QuestionTypeOperator(str, Enum):
    EQ = "="
    NE = "!="
    LT = "<"
    LTE = "<="
    GT = ">"
    GTE = ">="
    BETWEEN = "between"
