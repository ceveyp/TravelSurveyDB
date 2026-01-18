from enum import Enum


class QuestionDataType(str, Enum):
    BOOLEAN = "boolean"
    INTEGER = "number"
    FLOAT = "float"
    TEXT = "text"


class QuestionTypeOperator(str, Enum):
    EQ = "="
    NE = "!="
    LT = "<"
    LTE = "<="
    GT = ">"
    GTE = ">="
    BETWEEN = "between"
