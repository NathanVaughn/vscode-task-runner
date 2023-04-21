def stringify(value: str | int | float | bool) -> str:
    """
    Make sure the incoming value is close enough to a string, and convert it.
    """

    if not isinstance(value, (str, int, float, bool)):
        raise ValueError(f"Value '{value}' is not a string/number/boolean")

    return str(value)
