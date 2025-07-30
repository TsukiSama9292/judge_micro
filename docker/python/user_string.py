def solve(text: str, count: int) -> tuple:
    """
    String manipulation function.
    Convert text to uppercase and count characters.
    """
    new_text = text.upper()
    new_count = len(new_text)
    return (new_text, new_count, True)
