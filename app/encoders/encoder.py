from typing import Dict

SHUFFLED_ALPHABET = (
    "mn6WvK8RtQpZsY1bF4eO9wGzMxjD2Ie5qL7E0NxJcUhAlVaTu3CPkSydgrHiBf"
)

BASE = len(SHUFFLED_ALPHABET)

CHARINDEX = {
    char : idx for idx, char in enumerate(SHUFFLED_ALPHABET)
}

assert len(SHUFFLED_ALPHABET) == 62
assert len(set(CHARINDEX)) == 62


def encode_base62(number: int) -> str:
    if not isinstance(number, int):
        raise TypeError(f"Expected int, got {type(number)}")
    if number < 0:
        raise ValueError(f"Expected non-negative integer, got {number}")
    if number == 0:
        return SHUFFLED_ALPHABET[0]

