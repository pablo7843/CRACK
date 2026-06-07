#!/usr/bin/env python3
"""
Utility: generate hashes for a password.
Use to create test cases for crack.py.

Usage:
    python generate_hash.py "mypassword"
    python generate_hash.py "mypassword" --algo sha256
    python generate_hash.py "mypassword" --algo bcrypt --rounds 10
"""
import argparse
import hashlib
import sys

try:
    import bcrypt
    HAS_BCRYPT = True
except ImportError:
    HAS_BCRYPT = False

try:
    from rich.console import Console
    from rich.table import Table
    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False


def main():
    parser = argparse.ArgumentParser(
        description="Generate password hashes for crack.py testing"
    )
    parser.add_argument("password", help="Password to hash")
    parser.add_argument(
        "--algo",
        choices=["all", "md5", "sha1", "sha256", "sha512", "bcrypt"],
        default="all",
    )
    parser.add_argument(
        "--rounds", type=int, default=12,
        help="bcrypt work factor (default: 12)"
    )
    parser.add_argument("--save", metavar="FILE", help="Append hashes to file")
    args = parser.parse_args()

    pw = args.password.encode("utf-8")
    results = {}

    if args.algo in ("all", "md5"):
        results["MD5"] = hashlib.md5(pw).hexdigest()
    if args.algo in ("all", "sha1"):
        results["SHA-1"] = hashlib.sha1(pw).hexdigest()
    if args.algo in ("all", "sha256"):
        results["SHA-256"] = hashlib.sha256(pw).hexdigest()
    if args.algo in ("all", "sha512"):
        results["SHA-512"] = hashlib.sha512(pw).hexdigest()
    if args.algo in ("all", "bcrypt"):
        if HAS_BCRYPT:
            salt = bcrypt.gensalt(rounds=args.rounds)
            results["bcrypt"] = bcrypt.hashpw(pw, salt).decode()
        else:
            results["bcrypt"] = "[install bcrypt: pip install bcrypt]"

    if HAS_RICH:
        table = Table(title=f"Hashes for: [bold white]'{args.password}'[/]")
        table.add_column("Algorithm", style="cyan")
        table.add_column("Hash", style="yellow")
        for algo, h in results.items():
            table.add_row(algo, h)
        console.print(table)
    else:
        print(f"Password: {args.password}")
        for algo, h in results.items():
            print(f"  {algo:<10}: {h}")

    if args.save:
        with open(args.save, "a", encoding="utf-8") as f:
            for algo, h in results.items():
                f.write(f"{algo}:{h}:{args.password}\n")
        print(f"\nSaved to {args.save}")


if __name__ == "__main__":
    main()
