"""
encoder.py - Bijective Base62 Encoder / Decoder using a shuffled alphabet.
"""

from typing import Dict

# 62 unique characters: a-z, A-Z, 0-9 deterministically shuffled.
# CRITICAL: Never modify this string once URLs are written to the database,
# or existing short codes will decode to incorrect IDs.
SHUFFLED_ALPHABET = (
    "mn6WvK8RtQpZsY1bF4eO9wGzMxjD2Ie5qL7E0NxJcUhAlVaTu3CPkSydgrHiBf"
)

BASE = len(SHUFFLED_ALPHABET)  # 62

# Pre-computed reverse lookup table for O(1) character-to-index resolution
CHAR_TO_INDEX: Dict[str, int] = {
    char: idx for idx, char in enumerate(SHUFFLED_ALPHABET)
}

# Safety check during module import: ensure alphabet is exactly 62 unique chars
assert len(SHUFFLED_ALPHABET) == 62, "Alphabet must be exactly 62 characters"
assert len(set(SHUFFLED_ALPHABET)) == 62, "Alphabet characters must be unique"


def encode_base62(num: int) -> str:
    """
    Converts a positive integer into a shuffled Base62 string.

    Args:
        num: Non-negative integer (e.g., ticket ID from RangeManager).

    Returns:
        Bijective Base62 encoded string.
    """
    if not isinstance(num, int):
        raise TypeError(f"Expected int, got {type(num).__name__}")
    if num < 0:
        raise ValueError(f"Cannot encode negative integer: {num}")
    if num == 0:
        return SHUFFLED_ALPHABET[0]

    digits = []
    while num > 0:
        num, remainder = divmod(num, BASE)
        digits.append(SHUFFLED_ALPHABET[remainder])

    # Reversing because least significant digit was appended first
    return "".join(reversed(digits))


def decode_base62(code: str) -> int:
    """
    Converts a Base62 string back into its original integer ID.

    Args:
        code: Base62 encoded string.

    Returns:
        Original integer ID.
    """
    if not isinstance(code, str) or not code:
        raise ValueError("Code must be a non-empty string.")

    num = 0
    for char in code:
        idx = CHAR_TO_INDEX.get(char)
        if idx is None:
            raise ValueError(f"Invalid Base62 character: '{char}'")
        num = num * BASE + idx

    return num