import re
from datetime import date, datetime

from datavane.models import Candidate, InferredType

NULL_VALUES = ["", "null", None]

# Regular expressions for type-recognition patterns
BOOL_PATTERN = re.compile(r"true|false")
NORMAL_INT_PATTERN = re.compile(r"[+-]?\d+")
INT_LEADING_ZERO_PATTERN = re.compile(r"[+-]?0+\d+")
NORMAL_FLOAT_PATTERN = re.compile(r"[+-]?(?:\d+\.\d+|\.\d+)")
LEADING_ZERO_FLOAT_PATTERN = re.compile(r"[+-]?0+\d+\.\d+[eE]?[+-]?\d+")
FLOAT_SCIENTIFIC_NOTATION_PATTERN = re.compile(
    r"[+-]?(?:\d+(?:\.\d+)?|\.\d+)[eE][+-]?\d+"
)


# todo Document all this funtions
def normalize_value(val: str | None) -> str | None:
    """Strips all unnecesary whitespacaes from a string to normalize the value.

    Args:
        val (str | None): String that may contain whitespaces at the beginning or end.

    Returns:
        str|None: String with all whitespaces stripped. Returns None if
          the original value is None.
    """
    if val is None:
        return None

    return val.strip()


def is_null_value(val: str | None) -> bool:
    """Checks if a value is listed as NULL in NULL_VALUES.

    Args:
        val (str | None): Original string from the data dictionary.

    Returns:
        bool: True if val is cosidered null according to NULL_VALUES list.
    """
    if val is None:
        return True

    return val.lower() in NULL_VALUES


def detect_bool(val: str) -> bool:
    """Checks if val is recognized as a boolean pattern.

    Args:
        val (str): Original string from data

    Returns:
        bool: Returns True if val is a boolean.
    """
    return BOOL_PATTERN.fullmatch(val.lower()) is not None


def detect_int(val: str) -> str:
    """Checks if val is recognized as an int pattern.

    Args:
        val (str): Data string from the original data

    Returns:
        str: Returns an evidence set for int patterns if val is recognized as an int.
    """
    evidence = set()

    if NORMAL_INT_PATTERN.fullmatch(val):
        evidence.add("normal")

    if INT_LEADING_ZERO_PATTERN.fullmatch(val):
        evidence.add("leading_zero")

    return evidence


def detect_float(val: str) -> str:
    """Checks if val is recognized as a float pattern.

    Args:
        val (str): Original string from the data

    Returns:
        str: Returns an evidence set for float patterns if val is recognized as float
    """
    evidence = set()

    if NORMAL_FLOAT_PATTERN.fullmatch(val):
        evidence.add("normal")

    if LEADING_ZERO_FLOAT_PATTERN.fullmatch(val):
        evidence.add("leading_zero")

    if FLOAT_SCIENTIFIC_NOTATION_PATTERN.fullmatch(val):
        evidence.add("scientific notation")

    return evidence


def detect_date(val: str) -> set[str]:
    """Checks if val is recognized as a date pattern. Date needs to be in ISO format.

    Args:
        val (str): Original string from the data

    Returns:
        set[str]: Returns a set of evidences for dates if val is recognized as a date.
    """
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", val):
        return set()

    try:
        date.fromisoformat(val)
    except ValueError:
        return set()

    return {"iso_date"}


def detect_datetime(val: str) -> set[str]:
    """Checks if val is recognized as a datetime pattern.
      Datetime needs to be in ISO format.

    Args:
        val (str): Original string from the data

    Returns:
        set[str]: Returns a set of evidences for datetime types if val is recognized
          as a datetime
    """
    pattern = (
        r"\d{4}-\d{2}-\d{2}"
        r"[T ]"
        r"\d{2}:\d{2}:\d{2}"
        r"(?:\.\d+)?"
        r"(?:Z|[+-]\d{2}:\d{2})?"
    )

    if not re.fullmatch(pattern, val):
        return set()

    normalized = val.replace("Z", "+00:00")

    try:
        datetime.fromisoformat(normalized)
    except ValueError:
        return set()

    return {"iso_datetime"}


def detect_candidates(val: str):
    """Infers type and evidence for val. If val is not recognized as any of the listed
      patterns, type will be set as str with no evidence as a fallback.

    Args:
        val (str): Original value from the data.

    Returns:
        _type_: Returns a Candidate object with inferred type and evidence.
        Type is set to str with no evidence if val is not recognized
          as any of the patterns listed.
    """
    if detect_bool(val):
        return Candidate(type=InferredType.BOOL)

    int_evidence = detect_int(val)
    if int_evidence:
        return Candidate(InferredType.INT, int_evidence)

    float_evidence = detect_float(val)
    if float_evidence:
        return Candidate(InferredType.FLOAT, float_evidence)

    datetime_evidence = detect_datetime(val)
    if datetime_evidence:
        return Candidate(InferredType.DATETIME, datetime_evidence)

    date_evidence = detect_date(val)
    if date_evidence:
        return Candidate(InferredType.DATE, date_evidence)

    return Candidate(type=InferredType.STR)
