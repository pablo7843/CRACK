"""
Password mutation rules — mirrors hashcat's rule engine basics.
Expand candidate passwords before hashing to cover common patterns.
"""

LEET_MAP = str.maketrans("aeiostAEIOST", "431057431057")

COMMON_SUFFIXES = [
    "1", "12", "123", "1234", "12345", "!", "!!", "!@#",
    "123!", "2023", "2024", "2025", "#1", "@1", "00",
]

COMMON_PREFIXES = ["1", "the", "my", "123", "go"]


def leet_speak(word: str) -> list:
    return [word.translate(LEET_MAP)]


def capitalize_variants(word: str) -> list:
    variants = {word.capitalize(), word.upper(), word.lower()}
    if len(word) > 1:
        variants.add(word[0].upper() + word[1:].lower())
    variants.discard(word)
    return list(variants)


def append_numbers(word: str) -> list:
    return [word + s for s in COMMON_SUFFIXES]


def prepend(word: str) -> list:
    return [p + word for p in COMMON_PREFIXES]


def duplicate(word: str) -> list:
    return [word + word]


def reverse(word: str) -> list:
    return [word[::-1]]


def leet_plus_suffix(word: str) -> list:
    leet = word.translate(LEET_MAP)
    return [leet + s for s in ["1", "123", "!"]]


RULES_MAP = {
    "leet":       [leet_speak],
    "caps":       [capitalize_variants],
    "suffix":     [append_numbers],
    "prefix":     [prepend],
    "dup":        [duplicate],
    "rev":        [reverse],
    "best":       [capitalize_variants, append_numbers, leet_speak],
    "all":        [leet_speak, capitalize_variants, append_numbers, prepend, duplicate, reverse],
}


def apply_rules(word: str, rule_fns: list) -> list:
    candidates = []
    for fn in rule_fns:
        candidates.extend(fn(word))
    return candidates
