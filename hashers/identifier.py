import re

HASH_PATTERNS = [
    ("MD5",      r"^[a-f0-9]{32}$"),
    ("SHA-1",    r"^[a-f0-9]{40}$"),
    ("SHA-256",  r"^[a-f0-9]{64}$"),
    ("SHA-512",  r"^[a-f0-9]{128}$"),
    ("bcrypt",   r"^\$2[ayb]\$\d{2}\$.{53}$"),
    ("MD5-crypt",r"^\$1\$.+\$.+$"),
    ("SHA-512-crypt", r"^\$6\$.+\$.+$"),
]

def identify(hash_str: str) -> list:
    h = hash_str.strip()
    found = [name for name, pat in HASH_PATTERNS if re.match(pat, h, re.IGNORECASE)]
    return found if found else ["Unknown"]
