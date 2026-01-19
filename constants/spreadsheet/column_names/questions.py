from enum import StrEnum


class QuestionsColumnNamesEnum(StrEnum):
    QUESTION_TEXT = 'Question'
    QUESTION_TYPE = 'Question Type'
    QUESTION_TYPE_NOTES = 'Question Type Notes'
    SCORE = 'Score'
    MAX_SCORE = 'Max Score'
    QUESTION_DEFINITION = 'Question Definition'
    SURVEY_SECTION = 'Survey Section'
    NOTES = 'Notes'
    MEASUREMENT = 'Measurement'
    ALGORITHM = 'Algohrythem'
    IS_RANGE = 'Is Range?'
    IN_ASSESSMENT = 'In Assessment?'
    APPLIES_PER_ROOM_TYPE = 'Applies Per Room Type?'
    OTC_CODE = 'OT Code Value'
    OTC_LIST_NAME = 'OT Code List Name'
    OTC_CATEGORY = 'OpenTravel Category Code'
