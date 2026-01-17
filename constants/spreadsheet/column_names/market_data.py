from enum import StrEnum


class MarketDataColumnNamesEnum(StrEnum):
    DISABILITY = 'Disability'
    IMPACTED = 'People (US Only)'
    IMPACTED_WORKFORCE = 'WorkForce (US Only)'
    LIKELIHOOD = 'Likelyhood'
    LABOR_STAT = 'Labor Stat'
    STATISTICS = 'Statistics'
    STATISTICS_SOURCE = 'Disablity Statistics Source (Likelyhood)'
    LABOR_SOURCE = 'Labor Source'
    DEFINITION = 'Definition'
    DEFINITION_SOURCE = 'Definition Source'
