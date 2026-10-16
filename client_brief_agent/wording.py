"""small bits of wording shared by the explanations and the brief, so both say the same thing."""
import math


def plural(n, word):
    return f"{n:.0f} {word}" if round(n) == 1 else f"{n:.0f} {word}s"


def tenure_phrase(months):
    """a zero must read as new, not as 'with the bank for 0 months'. none when it is not recorded."""
    if months is None or (isinstance(months, float) and math.isnan(months)):
        return None
    if round(months) == 0:
        return "joined this month"
    return f"with the bank for {plural(months, 'month')}" if months < 24 else \
        f"with the bank for {plural(months / 12, 'year')}"
