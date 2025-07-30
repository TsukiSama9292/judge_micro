def solve(numbers: list, sum_result: int) -> tuple:
    """
    Example solve function for list manipulation.
    Lists are mutable, so modifications persist.
    """
    # Modify the list in-place (this will persist)
    for i in range(len(numbers)):
        numbers[i] = numbers[i] * 2
    
    # Calculate sum
    calculated_sum = sum(numbers)
    
    # Return tuple: (modified_numbers, modified_sum_result, return_value)
    return (numbers, calculated_sum, True)
