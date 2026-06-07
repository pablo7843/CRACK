import time
from pathlib import Path
from hashers.algorithms import compute, verify_bcrypt, normalize_algo
from attacks.rules import apply_rules


def dictionary_attack(
    target_hash: str,
    algorithm: str,
    wordlist_path: str,
    rule_fns: list = None,
    progress_cb=None,
) -> tuple:
    """
    Crack target_hash via wordlist.

    Returns: (plaintext | None, attempts, elapsed_seconds)
    """
    target = target_hash.strip().lower()
    path = Path(wordlist_path)
    if not path.exists():
        raise FileNotFoundError(f"Wordlist not found: {wordlist_path}")

    algo = normalize_algo(algorithm)
    is_bcrypt = algo == "bcrypt"
    attempts = 0
    start = time.perf_counter()

    with open(path, encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            word = line.rstrip("\n\r")
            if not word:
                continue

            candidates = [word]
            if rule_fns:
                candidates.extend(apply_rules(word, rule_fns))

            for candidate in candidates:
                attempts += 1

                if is_bcrypt:
                    if verify_bcrypt(candidate, target_hash.strip()):
                        return candidate, attempts, time.perf_counter() - start
                else:
                    if compute(candidate, algo) == target:
                        return candidate, attempts, time.perf_counter() - start

                if progress_cb and attempts % 10_000 == 0:
                    elapsed = time.perf_counter() - start
                    speed = attempts / elapsed if elapsed > 0 else 0
                    progress_cb(attempts, speed, candidate)

    return None, attempts, time.perf_counter() - start
