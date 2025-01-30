from pydantic import constr

from ...definitions.constraints import MIN_STRING_LENGTH, MAX_STRING_LENGTH


def create_constrained_string() -> constr:
    """Create a constrained string type."""
    return constr(min_length=MIN_STRING_LENGTH, max_length=MAX_STRING_LENGTH)