def solve(numbers: list, target: int) -> tuple:
    """
    Advanced list sorting and search function.
    Sort the list and find target index.
    """
    numbers.sort()
    try:
        target_index = numbers.index(target)
    except ValueError:
        target_index = -1
    return (numbers, target_index, 0)
