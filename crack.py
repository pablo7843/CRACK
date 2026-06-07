#!/usr/bin/env python3
"""
crack.py -- Password Hash Cracker (Educational Tool)

Modes:
  Dictionary attack   : test wordlist entries + optional mutations
  Brute force         : exhaustive character-space enumeration
  Credential stuffing : simulate credential reuse attack
  Info                : explain hashing algorithms

Usage examples:
  python crack.py --hash 5f4dcc3b5aa765d61d8327deb882cf99 --algo MD5 --attack dict
  python crack.py --hash 5f4dcc3b5aa765d61d8327deb882cf99 --algo auto --attack dict --rules best
  python crack.py --hash <md5> --algo MD5 --attack brute --charset digits --max-len 6
  python crack.py --demo stuffing
  python crack.py --info
  python crack.py --lang es --hash <hash> --algo auto --attack dict
"""
import argparse
import sys
from pathlib import Path

from hashers.identifier import identify
from hashers.algorithms import normalize_algo
from attacks.dictionary import dictionary_attack
from attacks.brute_force import brute_force, estimate_keyspace, CHARSETS
from attacks.rules import RULES_MAP
from attacks.credential_stuffing import simulate_stuffing, DEFENSE_STRATEGIES, DEMO_LEAKED_DB
from utils.lang import t, set_lang, detect_lang
from utils.display import (
    console, print_banner, print_algo_table, print_result,
    print_hashcat_hint, print_keyspace_estimate,
    print_stuffing_results, print_defenses,
)

DEFAULT_WORDLIST = Path(__file__).parent / "wordlists" / "common.txt"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="crack.py",
        description="Password hash cracker -- educational tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    target = p.add_argument_group("Target")
    target.add_argument("--hash", dest="hash_str", metavar="HASH", help="Hash to crack")
    target.add_argument(
        "--algo",
        default="auto",
        help="Hash algorithm: MD5 | SHA-1 | SHA-256 | SHA-512 | bcrypt | auto (default: auto)",
    )
    target.add_argument(
        "--hash-file", metavar="FILE",
        help="File with one hash per line (same algorithm for all)",
    )

    attack = p.add_argument_group("Attack")
    attack.add_argument(
        "--attack", choices=["dict", "brute"], default="dict",
        help="Attack mode: dict (dictionary) | brute (brute force) (default: dict)",
    )
    attack.add_argument(
        "--wordlist", default=str(DEFAULT_WORDLIST),
        help=f"Wordlist path (default: {DEFAULT_WORDLIST})",
    )
    attack.add_argument(
        "--rules",
        choices=list(RULES_MAP.keys()),
        help="Apply mutation rules: leet | caps | suffix | prefix | dup | rev | best | all",
    )

    brute_g = p.add_argument_group("Brute Force options")
    brute_g.add_argument(
        "--charset",
        choices=list(CHARSETS.keys()),
        default="alphanum",
        help="Character set (default: alphanum)",
    )
    brute_g.add_argument("--min-len", type=int, default=1, help="Min password length (default: 1)")
    brute_g.add_argument("--max-len", type=int, default=6, help="Max password length (default: 6)")

    misc = p.add_argument_group("Misc")
    misc.add_argument("--info", action="store_true", help="Show hashing algorithm reference table")
    misc.add_argument(
        "--demo", metavar="DEMO",
        choices=["stuffing"],
        help="Run educational demo: stuffing",
    )
    misc.add_argument("--hashcat", action="store_true", help="Print equivalent hashcat commands")
    misc.add_argument("--keyspace", action="store_true", help="Show brute force keyspace estimate")
    misc.add_argument("--quiet", action="store_true", help="Suppress progress output")
    misc.add_argument(
        "--lang", choices=["en", "es"],
        help="Language override: en | es (default: auto-detect from system locale)",
    )

    return p


def resolve_algo(hash_str: str, algo_arg: str) -> str:
    if algo_arg.lower() != "auto":
        return normalize_algo(algo_arg)
    candidates = identify(hash_str)
    if len(candidates) == 1 and candidates[0] != "Unknown":
        console.print(f"[dim]{t('auto_detected', candidates[0])}[/dim]")
        return candidates[0]
    console.print(f"[yellow]{t('hash_could_be', ', '.join(candidates))}[/]")
    if "Unknown" in candidates:
        sys.exit(1)
    return candidates[0]


def crack_single(hash_str: str, algo: str, args) -> None:
    rule_fns = RULES_MAP.get(args.rules, []) if args.rules else []

    if args.hashcat:
        print_hashcat_hint(hash_str, algo, args.wordlist)

    progress = None if args.quiet else lambda a, s, w: console.print(
        f"  [dim]{t('progress_fmt', f'{a:,}', f'{s:,.0f}', repr(w))}[/dim]",
        end="\r",
    )

    if args.attack == "dict":
        console.print(
            f"\n[bold]{t('dict_attack_header')}[/] | "
            f"{t('algo_label')}=[yellow]{algo}[/] | "
            f"{t('wordlist_label')}=[cyan]{args.wordlist}[/]"
        )
        if rule_fns:
            console.print(f"  {t('rules_label')}: [yellow]{args.rules}[/]")
        plaintext, attempts, elapsed = dictionary_attack(
            hash_str, algo, args.wordlist,
            rule_fns=rule_fns,
            progress_cb=progress,
        )
        if not args.quiet:
            console.print()
        print_result(plaintext, algo, attempts, elapsed, attack_type=t("attack_type_dict"))

    elif args.attack == "brute":
        if args.keyspace or not args.quiet:
            print_keyspace_estimate(args.charset, args.min_len, args.max_len)
        console.print(
            f"\n[bold]{t('brute_attack_header')}[/] | "
            f"{t('algo_label')}=[yellow]{algo}[/] | "
            f"{t('charset_label')}=[cyan]{args.charset}[/] | "
            f"{t('len_label')}=[cyan]{args.min_len}-{args.max_len}[/]"
        )
        plaintext, attempts, elapsed = brute_force(
            hash_str, algo,
            charset=args.charset,
            min_len=args.min_len,
            max_len=args.max_len,
            progress_cb=progress,
        )
        if not args.quiet:
            console.print()
        print_result(plaintext, algo, attempts, elapsed, attack_type=t("attack_type_brute"))


def demo_stuffing() -> None:
    import hashlib
    console.print(f"\n[bold cyan]{t('stuffing_title')}[/]\n")
    console.print(t("stuffing_scenario") + "\n")

    # Build target service hashes — same passwords reused by 3 of 5 users
    target_hashes = {
        user: hashlib.sha256(pw.encode()).hexdigest()
        for user, pw in DEMO_LEAKED_DB
    }
    # 2 users changed their passwords on ServiceB
    target_hashes["diana@example.com"] = hashlib.sha256(b"uniquepassword!9").hexdigest()
    target_hashes["eve@example.com"] = hashlib.sha256(b"correct-horse-battery").hexdigest()

    console.print(f"[dim]{t('stuffing_hashes_label')}[/dim]")
    for user, h in target_hashes.items():
        console.print(f"  {user:<30} {h[:32]}...")

    console.print(f"\n[yellow]{t('stuffing_running')}[/]\n")
    hits = simulate_stuffing(DEMO_LEAKED_DB, "SHA-256", target_hashes)
    print_stuffing_results(hits, len(DEMO_LEAKED_DB))

    console.print(f"\n[bold cyan]{t('stuffing_defend')}[/]")
    print_defenses(DEFENSE_STRATEGIES)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # Set language before any output is produced
    lang = args.lang if args.lang else detect_lang()
    set_lang(lang)

    print_banner()

    if args.info:
        print_algo_table()
        return

    if args.demo:
        if args.demo == "stuffing":
            demo_stuffing()
        return

    if not args.hash_str and not args.hash_file:
        from utils.interactive import run_interactive
        run_interactive()
        return

    if args.hash_file:
        path = Path(args.hash_file)
        if not path.exists():
            console.print(f"[red]{t('err_hash_file_not_found', path)}[/]")
            sys.exit(1)
        hashes = [
            line.strip() for line in path.read_text().splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        console.print(f"\n[bold]{t('batch_cracking', len(hashes), path)}[/]\n")
        for i, h in enumerate(hashes, 1):
            console.print(f"\n[bold cyan]{t('hash_n_of_m', i, len(hashes))}[/] {h}")
            algo = resolve_algo(h, args.algo)
            try:
                crack_single(h, algo, args)
            except Exception as e:
                console.print(f"[red]{t('err_generic', e)}[/]")
        return

    algo = resolve_algo(args.hash_str, args.algo)
    try:
        crack_single(args.hash_str, algo, args)
    except Exception as e:
        console.print(f"[red]{t('err_generic', e)}[/]")
        sys.exit(1)


if __name__ == "__main__":
    main()
