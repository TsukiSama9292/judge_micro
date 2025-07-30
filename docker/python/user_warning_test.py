def solve(data: list, result: str) -> tuple:
    """
    Warning test function.
    This function uses deprecated features to generate warnings.
    """
    import warnings
    warnings.warn("This is a test warning", DeprecationWarning)
    
    new_result = "warning"
    return (data, new_result)
