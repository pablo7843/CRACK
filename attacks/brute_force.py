import string
import itertools
import time
from hashers.algorithms import compute, normalize_algo

CHARSETS = {
    "digits":    string.digits,
    "lower":     string.ascii_lowercase,
    "upper":     string.ascii_uppercase,
    "alpha":     string.ascii_letters,
    "alphanum":  string.ascii_letters + string.digits,
    "hex":       "0123456789abcdef",
    "special":   string.punctuation,
    "full":      string.ascii_letters + string.digits + string.punctuation,
}


def brute_force(
    target_hash: str,
    algorithm: str,
    charset: str = "alphanum",
    min_len: int = 1,
    max_len: int = 6,
    progress_cb=None,
) -> tuple:
    """
    CPU brute force — exhaustive enumeration.
    Practical for short passwords (<= 6 chars) or when combined with a mask.
    For longer passwords, use hashcat with GPU.

    Returns: (plaintext | None, attempts, elapsed_seconds)
    """
    target = target_hash.strip().lower()
    algo = normalize_algo(algorithm)

    if algo == "bcrypt":
        raise ValueError("Brute force against bcrypt is not practical — use dictionary attack.")

    chars = CHARSETS.get(charset, charset)
    attempts = 0
    start = time.perf_counter()

    for length in range(min_len, max_len + 1):
        for combo in itertools.product(chars, repeat=length):
            candidate = "".join(combo)
            attempts += 1
            if compute(candidate, algo) == target:
                return candidate, attempts, time.perf_counter() - start

            if progress_cb and attempts % 50_000 == 0:
                elapsed = time.perf_counter() - start
                speed = attempts / elapsed if elapsed > 0 else 0
                progress_cb(attempts, speed, candidate)

    return None, attempts, time.perf_counter() - start


def estimate_keyspace(charset: str, min_len: int, max_len: int) -> int:
    chars = CHARSETS.get(charset, charset)
    n = len(chars)
    return sum(n ** length for length in range(min_len, max_len + 1))
