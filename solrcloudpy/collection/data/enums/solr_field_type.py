from enum import StrEnum


class SolrFieldType(StrEnum):
    STRING = 'string'

    BOOLEAN = 'boolean'

    INTEGER = 'pint'
    LONG = 'plong'
    FLOAT = 'pfloat'
    DOUBLE = 'pdouble'

    DATE = 'pdate'

    BINARY = 'binary'

    TEXT_GENERAL = 'text_general'
