import hashlib
import bcrypt

# Static algorithm metadata — notes/descriptions live in utils/lang.py (i18n)
ALGO_INFO = {
    "MD5": {
        "bits": 128,
        "hashcat_mode": 0,
        "broken": True,
        "year": 1991,
    },
    "SHA-1": {
        "bits": 160,
        "hashcat_mode": 100,
        "broken": True,
        "year": 1995,
    },
    "SHA-256": {
        "bits": 256,
        "hashcat_mode": 1400,
        "broken": False,
        "year": 2001,
    },
    "SHA-512": {
        "bits": 512,
        "hashcat_mode": 1700,
        "broken": False,
        "year": 2001,
    },
    "bcrypt": {
        "bits": 184,
        "hashcat_mode": 3200,
        "broken": False,
        "year": 1999,
    },
    "Argon2id": {
        "bits": 256,
        "hashcat_mode": 13400,
        "broken": False,
        "year": 2015,
    },
}

ALGO_NAMES = {
    "md5":     "MD5",
    "sha1":    "SHA-1",
    "sha-1":   "SHA-1",
    "sha256":  "SHA-256",
    "sha-256": "SHA-256",
    "sha512":  "SHA-512",
    "sha-512": "SHA-512",
    "bcrypt":  "bcrypt",
}


def normalize_algo(name: str) -> str:
    return ALGO_NAMES.get(name.lower(), name)


def compute(password: str, algorithm: str) -> str | None:
    pw = password.encode("utf-8", errors="replace")
    algo = normalize_algo(algorithm)
    if algo == "MD5":
        return hashlib.md5(pw).hexdigest()
    elif algo == "SHA-1":
        return hashlib.sha1(pw).hexdigest()
    elif algo == "SHA-256":
        return hashlib.sha256(pw).hexdigest()
    elif algo == "SHA-512":
        return hashlib.sha512(pw).hexdigest()
    return None


def verify_bcrypt(password: str, hash_str: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hash_str.encode("utf-8"))
    except Exception:
        return False


def hash_bcrypt(password: str, rounds: int = 12) -> str:
    salt = bcrypt.gensalt(rounds=rounds)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode()
