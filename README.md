# CRACK — Password Hash Cracker

```
  +--------------------------------------------------+
  |   ____  ____      _      ____  _  __            |
  |  / ___||  _ \    / \    / ___|| |/ /            |
  | | |    | |_) |  / _ \  | |    | ' /             |
  | | |___ |  _ <  / ___ \ | |___ | . \             |
  |  \____||_| \_\/_/   \_\ \____||_|\_\            |
  |                                                 |
  |  >>  Password Hash Cracker        v1.0  <<      |
  |  >>  Dictionary | BruteForce | Stuffing  <<     |
  +--------------------------------------------------+
```

> **Educational tool** for learning password hashing, cracking techniques, and credential security.
> For CTF challenges, cybersecurity courses, and personal learning.
> **Never use against systems you don't own or have explicit authorization to test.**

---

## Features

| Feature | Description |
|---------|-------------|
| **Dictionary attack** | Test wordlist entries against a hash, with optional mutation rules |
| **Brute force** | Exhaustive character-space enumeration with configurable charset and length |
| **Mutation rules** | leet speak, capitalization, number suffixes, prefixes, duplicates, reverse |
| **Auto hash detection** | Identifies MD5, SHA-1, SHA-256, SHA-512, bcrypt automatically by pattern |
| **Batch cracking** | Crack multiple hashes from a file in one run |
| **Interactive mode** | Arrow-key guided menu — no flags needed |
| **Hash generator** | Generate hashes from any plaintext password |
| **Hashcat commands** | Get GPU-accelerated equivalent commands for any hash |
| **Keyspace estimator** | Calculate candidates and estimated time before running brute force |
| **Credential stuffing demo** | Simulate a real-world password reuse attack + defense strategies |
| **Algorithm info table** | Security overview of MD5, SHA-1, SHA-256, SHA-512, bcrypt, Argon2id |
| **Bilingual EN / ES** | Full internationalization — auto-detects system locale, override with `--lang` |

---

## Supported Algorithms

| Algorithm | Bits | Broken? | Hashcat Mode | Notes |
|-----------|------|---------|--------------|-------|
| MD5 | 128 | YES | 0 | Fully broken since 2004. ~50B cracks/s on GPU |
| SHA-1 | 160 | YES | 100 | SHAttered attack 2017. Deprecated by NIST |
| SHA-256 | 256 | No | 1400 | Secure but no salt — vulnerable to rainbow tables |
| SHA-512 | 512 | No | 1700 | Stronger but still no built-in salt |
| bcrypt | 184 | No | 3200 | Built-in salt + work factor. Recommended for passwords |
| Argon2id | 256 | No | 13400 | PHC winner 2015. Memory-hard. Current best practice |

---

## Installation

```bash
# Clone the repo
git clone https://github.com/YOURUSERNAME/crack-pwssd-hashes.git
cd crack-pwssd-hashes

# Install dependencies
pip install -r requirements.txt
```

**Requirements:** Python 3.10+ · `rich` · `bcrypt` · `questionary`

---

## Usage

### Interactive mode (recommended for beginners)

```bash
python crack.py
```

Launches a guided arrow-key menu with all features:

```
What do you want to do?
  > Crack a single hash
    Crack a hash file (multiple hashes)
    ─────────────────────────────────
    Generate hashes from a password
    Show hashcat commands for a hash
    Keyspace estimator (brute force)
    ─────────────────────────────────
    Credential stuffing demo
    View algorithm info table
    ─────────────────────────────────
    Change language
    Exit
```

---

### CLI mode (for scripting and power users)

#### Crack a single hash

```bash
# Auto-detect algorithm
python crack.py --hash 5f4dcc3b5aa765d61d8327deb882cf99 --algo auto --attack dict

# Specify algorithm
python crack.py --hash 5f4dcc3b5aa765d61d8327deb882cf99 --algo MD5 --attack dict

# With mutation rules (much more powerful)
python crack.py --hash <hash> --algo MD5 --attack dict --rules best
```

#### Mutation rules

| Rule | What it does |
|------|-------------|
| `leet` | a→4, e→3, i→1, o→0, s→5, t→7 |
| `caps` | Capitalize, UPPERCASE, lowercase variants |
| `suffix` | Append: 1, 12, 123, 1234, !, !!, 2024, 2025... |
| `prefix` | Prepend: 1, 123, the, my... |
| `dup` | Double the word: passwordpassword |
| `rev` | Reverse: drowssap |
| `best` | caps + suffix + leet (recommended) |
| `all` | All rules combined |

```bash
python crack.py --hash <hash> --algo MD5 --attack dict --rules best
python crack.py --hash <hash> --algo MD5 --attack dict --rules all
```

#### Brute force

```bash
# Digits only, up to 6 chars
python crack.py --hash <hash> --algo MD5 --attack brute --charset digits --max-len 6

# Lowercase letters, 1-4 chars
python crack.py --hash <hash> --algo MD5 --attack brute --charset lower --max-len 4

# Alphanumeric, 1-5 chars
python crack.py --hash <hash> --algo MD5 --attack brute --charset alphanum --max-len 5
```

Available charsets:

| Charset | Characters |
|---------|-----------|
| `digits` | 0-9 |
| `lower` | a-z |
| `upper` | A-Z |
| `alpha` | a-z + A-Z |
| `alphanum` | a-z + A-Z + 0-9 |
| `hex` | 0-9 + a-f |
| `special` | punctuation symbols |
| `full` | all of the above |

#### Batch crack (hash file)

```bash
python crack.py --hash-file hashes/samples.txt --algo MD5 --attack dict
```

Hash file format — one hash per line, `#` for comments:
```
# My test hashes
5f4dcc3b5aa765d61d8327deb882cf99
e10adc3949ba59abbe56e057f20f883e
```

#### Show hashcat commands (GPU)

```bash
python crack.py --hash <hash> --algo MD5 --hashcat
```

#### Algorithm info table

```bash
python crack.py --info
```

#### Credential stuffing demo

```bash
python crack.py --demo stuffing
```

#### Generate hashes for testing

```bash
# All algorithms
python generate_hash.py "mypassword"

# Specific algorithm
python generate_hash.py "mypassword" --algo sha256
python generate_hash.py "mypassword" --algo bcrypt --rounds 10

# Save to file (for use with --hash-file)
python generate_hash.py "mypassword" --save hashes/my_hashes.txt
```

---

### Language

```bash
# Spanish
python crack.py --lang es --hash <hash> --algo auto --attack dict

# English
python crack.py --lang en --hash <hash> --algo auto --attack dict

# Auto-detect from system locale (default)
python crack.py --hash <hash> --algo auto --attack dict

# Force Spanish via environment variable
$env:LANG = "es_ES"
python crack.py
```

---

### Other flags

| Flag | Description |
|------|-------------|
| `--quiet` | Suppress progress output |
| `--keyspace` | Show keyspace size before brute force |
| `--wordlist PATH` | Use a custom wordlist (e.g. rockyou.txt) |
| `--min-len N` | Minimum length for brute force (default: 1) |
| `--max-len N` | Maximum length for brute force (default: 6) |

---

## Typical CTF Workflow

```bash
# 1. Unknown hash — auto-detect and try wordlist
python crack.py --hash d8578edf8458ce06fbc5bb76a58c5ca4 --algo auto --attack dict

# 2. Not in wordlist — add mutations
python crack.py --hash <hash> --algo MD5 --attack dict --rules best

# 3. Still nothing — short brute force
python crack.py --hash <hash> --algo MD5 --attack brute --charset alphanum --max-len 5

# 4. Need GPU power — get hashcat command
python crack.py --hash <hash> --algo MD5 --hashcat
```

For GPU cracking, download [hashcat](https://hashcat.net) and [rockyou.txt](https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt).

---

## Project Structure

```
crack-pwssd-hashes/
│
├── crack.py                  # Main CLI entry point
├── generate_hash.py          # Hash generator utility
├── requirements.txt
│
├── hashers/
│   ├── identifier.py         # Auto-detect hash type by regex pattern
│   └── algorithms.py         # compute(), verify_bcrypt(), ALGO_INFO
│
├── attacks/
│   ├── dictionary.py         # Wordlist-based attack engine
│   ├── brute_force.py        # Exhaustive enumeration (itertools.product)
│   ├── rules.py              # Password mutation rules
│   └── credential_stuffing.py  # Stuffing simulation + DEFENSE_STRATEGIES
│
├── utils/
│   ├── display.py            # Rich-based UI (tables, panels, progress)
│   ├── lang.py               # i18n — all EN/ES strings + t() + detect_lang()
│   └── interactive.py        # Guided interactive mode (questionary)
│
├── wordlists/
│   └── common.txt            # ~100 most common passwords (sample)
│
└── hashes/
    └── samples.txt           # Verified test hashes (answers in common.txt)
```

---

## What You Learn

- **Why MD5 and SHA-1 are broken** — collision attacks, GPU crack speeds
- **Why raw SHA-256/SHA-512 are unsafe for passwords** — no salt, rainbow table vulnerability  
- **How bcrypt/Argon2 defend against GPU attacks** — work factor, built-in salt
- **Dictionary attack mechanics** — wordlists, mutation rules, why "p@ssw0rd" isn't safe
- **Brute force complexity** — keyspace size, why password length matters more than complexity
- **Credential stuffing** — how password reuse across services enables attacks
- **Defense strategies** — MFA, rate limiting, HaveIBeenPwned, device fingerprinting

---

## Disclaimer

This tool is intended **exclusively** for:
- CTF (Capture The Flag) competitions
- Academic cybersecurity coursework
- Testing your own systems
- Understanding password security concepts

**Never use this tool against accounts, systems, or hashes you do not own or have explicit written authorization to test.** Unauthorized access is illegal in most jurisdictions.
