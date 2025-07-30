def solve(a: int, b: int) -> tuple:
    """
    Example solve function for basic integer manipulation.
    Since int is immutable in Python, we return the modified values.
    """
    new_a = a * 2
    new_b = b + 5
    # Return tuple: (modified_a, modified_b, return_value)
    return (new_a, new_b, 0)
