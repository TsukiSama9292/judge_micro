def solve(x: int) -> tuple:
    """
    Error test function.
    This function is designed to fail with a runtime error.
    """
    result = x / 0  # Intentional division by zero
    return (result, 0)
