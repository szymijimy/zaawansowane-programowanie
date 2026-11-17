import re
from collections import Counter
from typing import Any

__all__ = [
    "is_palindrome",
    "fibonacci",
    "count_vowels",
    "calculate_discount",
    "flatten_list",
    "word_frequencies",
    "is_prime",
]


def is_palindrome(text: str) -> bool:
    cleaned = "".join(text.split()).lower()
    return cleaned == cleaned[::-1]


def fibonacci(n: int) -> int:
    if n < 0:
        raise ValueError("n must be non-negative")
    if n < 2:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def count_vowels(text: str) -> int:
    vowels = set("aeiouyąęó")
    normalized = text.lower()
    count = 0
    for idx, char in enumerate(normalized):
        if char in vowels:
            if (
                char == "i"
                and idx > 0
                and normalized[idx - 1].isalpha()
                and normalized[idx - 1] not in vowels
                and idx + 1 < len(normalized)
                and normalized[idx + 1] in vowels
            ):
                continue
            count += 1
    return count


def calculate_discount(price: float, discount: float) -> float:
    if not (0.0 <= discount <= 1.0):
        raise ValueError("Discount must be between 0.0 and 1.0")
    if price < 0.0:
        raise ValueError("Price cannot be negative")
    return float(price * (1.0 - discount))


def flatten_list(nested_list: list[Any]) -> list[Any]:
    result: list[Any] = []
    for item in nested_list:
        if isinstance(item, list):
            result.extend(flatten_list(item))
        else:
            result.append(item)
    return result


def word_frequencies(text: str) -> dict[str, int]:
    words = re.findall(r"\w+", text.lower())
    return dict(Counter(words))


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True
