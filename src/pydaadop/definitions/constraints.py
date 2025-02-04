"""
This module defines constraints used throughout the application.

These constraints are used to validate string lengths in various parts of the application.

Attributes:
    MIN_STRING_LENGTH (int): The minimum allowed length for strings.
    MAX_STRING_LENGTH (int): The maximum allowed length for strings.

Example:
    ```python
    from myapp.definitions.constraints import MIN_STRING_LENGTH, MAX_STRING_LENGTH

    def validate_string_length(s: str) -> bool:
        return MIN_STRING_LENGTH <= len(s) <= MAX_STRING_LENGTH
    ```
"""

MIN_STRING_LENGTH = 1
MAX_STRING_LENGTH = 100