from enum import StrEnum


class FieldTypeClass(StrEnum):
    STRING = 'string'
    STRINGS = 'strings'

    BOOLEAN = 'boolean'
    BOOLEANS = 'booleans'

    INTEGER = 'pint'
    INTEGERS = 'pints'
    LONG = 'plong'
    LONGS = 'plongs'
    FLOAT = 'pfloat'
    FLOATS = 'pfloats'
    DOUBLE = 'pdouble'
    DOUBLES = 'pdoubles'

    DATE = 'pdate'
    DATES = 'pdates'

    BINARY = 'binary'

    TEXT_GENERAL = 'text_general'

    IGNORED = 'ignored'
    RANDOM = 'random'
    RANK = 'rank'
