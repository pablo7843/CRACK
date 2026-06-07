"""
Credential Stuffing — Educational Demo

Concept: attackers take (username, plaintext_password) pairs leaked from
Service A and test them against Service B. Works because users reuse passwords.

This module simulates the attack + demonstrates detection strategies.
"""

from hashers.algorithms import compute, normalize_algo


def simulate_stuffing(
    leaked_pairs: list,
    algorithm: str,
    target_hashes: dict,
) -> list:
    """
    leaked_pairs : [(username, plaintext_password), ...]
    target_hashes: {username: hash_string, ...}   <- hashes from target service
    Returns      : [(username, password), ...] that matched
    """
    algo = normalize_algo(algorithm)
    hits = []
    for username, password in leaked_pairs:
        if username not in target_hashes:
            continue
        computed = compute(password, algo)
        if computed and computed == target_hashes[username].lower():
            hits.append((username, password))
    return hits


DEFENSE_STRATEGIES = [
    {
        "name": "Password Hashing (Argon2id / bcrypt)",
        "impact": "Critical",
        "detail": (
            "Slow-by-design algorithms make GPU cracking impractical. "
            "Even if DB leaks, plaintext recovery is expensive."
        ),
    },
    {
        "name": "Multi-Factor Authentication (MFA)",
        "impact": "Critical",
        "detail": "Correct credentials alone not enough. OTP/FIDO2 required.",
    },
    {
        "name": "Rate Limiting + Lockout",
        "impact": "High",
        "detail": "Limit failed attempts per IP/account. Block after N failures.",
    },
    {
        "name": "HaveIBeenPwned check at registration",
        "impact": "High",
        "detail": (
            "Reject passwords found in known breach datasets. "
            "HIBP k-anonymity API: send first 5 chars of SHA-1 only."
        ),
    },
    {
        "name": "CAPTCHA on login",
        "impact": "Medium",
        "detail": "Stops automated stuffing bots without human interaction.",
    },
    {
        "name": "Device Fingerprinting",
        "impact": "Medium",
        "detail": "Flag logins from unknown devices/IPs even with correct credentials.",
    },
    {
        "name": "Unique salts per password",
        "impact": "High",
        "detail": (
            "Rainbow table attacks fail. Each password needs individual cracking. "
            "bcrypt/Argon2 handle this automatically."
        ),
    },
]

DEMO_LEAKED_DB = [
    ("alice@example.com", "password123"),
    ("bob@example.com", "qwerty"),
    ("charlie@example.com", "letmein"),
    ("diana@example.com", "sunshine"),
    ("eve@example.com", "iloveyou"),
]
