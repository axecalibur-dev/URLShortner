from typing import Dict

SHUFFLED_ALPHABET = (
    "mn6WvK8RtQpZsY1bF4eO9wGzMxjD2Io5qL7E0NxJcUhAlVaTu3CPkSydgrHiBf"
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


    digits = []

    while number > 0:
        number , remainder = divmod(number, BASE)
        digits.append(SHUFFLED_ALPHABET[remainder])



    return "".join(reversed(digits))



def deccode_base62(code:str) -> int:
    if not isinstance(code, str) or not code:
        raise TypeError(f"Expected str, got {type(code)}")

    num = 0
    for char in code:
        digit = SHUFFLED_ALPHABET.index(char)
        if digit is None:
            raise ValueError(f"Invalid character {char}")
        num = num * BASE + digit


    return num