def solve(n: int, factorial: int) -> tuple:
    """
    Example solve function for factorial calculation.
    Since int is immutable in Python, we return the modified values.
    """
    result = 1
    for i in range(1, n + 1):
        result *= i
    # Return tuple: (modified_n, modified_factorial, return_value)
    return (n, result, 0)
