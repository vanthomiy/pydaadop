"""
This module provides utilities for creating constrained string types using Pydantic.

Functions:
    create_constrained_string: Creates a constrained string type with specified minimum and maximum lengths.
"""

from pydantic import constr
from ...definitions.constraints import MIN_STRING_LENGTH, MAX_STRING_LENGTH

def create_constrained_string() -> constr:
    """
    Creates a constrained string type with specified minimum and maximum lengths.

    This function uses the `constr` type from Pydantic to create a string type
    that enforces minimum and maximum length constraints.

    Returns:
        constr: A constrained string type.

    Example:
        >>> ConstrainedStr = create_constrained_string()
        >>> ConstrainedStr('example')  # Valid if 'example' meets length constraints
        'example'
    """
    return constr(min_length=MIN_STRING_LENGTH, max_length=MAX_STRING_LENGTH)