"""
Interactive guided mode for crack.py.
Launched automatically when no CLI arguments are provided.
All prompts are bilingual via utils/lang.py.
"""
import argparse
import hashlib
import sys
from pathlib import Path

from utils.lang import t, set_lang
from utils.display import console, print_algo_table, print_hashcat_hint, print_keyspace_estimate

DEFAULT_WORDLIST = str(Path(__file__).parent.parent / "wordlists" / "common.txt")

# Sentinel: "no rules selected" — avoids collision with None (= user pressed Ctrl+C)
_NO_RULES = "__none__"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _q():
    """Return questionary module, or exit with install hint."""
    try:
        import questionary
        return questionary
    except ImportError:
        console.print(
            "[red]questionary not installed.[/]\n"
            "Run: [bold]pip install questionary[/]"
        )
        sys.exit(1)


def _algo_choices(q):
    """Reusable algorithm choice list."""
    return [
        q.Choice(t("prompt_algo_auto"), value="auto"),
        q.Choice("MD5",     value="MD5"),
        q.Choice("SHA-1",   value="SHA-1"),
        q.Choice("SHA-256", value="SHA-256"),
        q.Choice("SHA-512", value="SHA-512"),
        q.Choice("bcrypt",  value="bcrypt"),
    ]


def _dict_options(q, config: dict) -> dict | None:
    """Ask wordlist + rules for dictionary attack. Returns updated config or None."""
    from attacks.rules import RULES_MAP

    wordlist = q.text(
        t("prompt_wordlist"),
        default=DEFAULT_WORDLIST,
        validate=lambda v: t("err_file_missing", v) if not Path(v).exists() else True,
    ).ask()
    if wordlist is None:
        return None
    config["wordlist"] = wordlist

    rule_choices = [q.Choice(t("prompt_rules_none"), value=_NO_RULES)]
    rule_choices += [q.Choice(k, value=k) for k in RULES_MAP]
    rules_val = q.select(t("prompt_rules"), choices=rule_choices).ask()
    if rules_val is None:
        return None
    config["rules"] = None if rules_val == _NO_RULES else rules_val
    return config


def _brute_options(q, config: dict) -> dict | None:
    """Ask charset + lengths for brute force attack. Returns updated config or None."""
    from attacks.brute_force import CHARSETS

    charset = q.select(t("prompt_charset"), choices=list(CHARSETS)).ask()
    if charset is None:
        return None

    min_len = q.text(
        t("prompt_min_len"), default="1",
        validate=lambda v: t("err_invalid_number") if not v.isdigit() or int(v) < 1 else True,
    ).ask()
    if min_len is None:
        return None

    max_len = q.text(
        t("prompt_max_len"), default="6",
        validate=lambda v: t("err_invalid_number") if not v.isdigit() or int(v) < 1 else True,
    ).ask()
    if max_len is None:
        return None

    config["charset"] = charset
    config["min_len"] = int(min_len)
    config["max_len"] = int(max_len)
    return config


# ---------------------------------------------------------------------------
# Flow: crack single hash
# ---------------------------------------------------------------------------

def _ask_hash_config() -> dict | None:
    """Collect full config for cracking one hash. Returns dict or None if cancelled."""
    q = _q()

    hash_str = q.text(
        t("prompt_hash"),
        validate=lambda v: t("err_empty_hash") if not v.strip() else True,
    ).ask()
    if hash_str is None:
        return None

    algo = q.select(t("prompt_algo"), choices=_algo_choices(q)).ask()
    if algo is None:
        return None

    attack = q.select(
        t("prompt_attack"),
        choices=[
            q.Choice(t("prompt_attack_dict"),  value="dict"),
            q.Choice(t("prompt_attack_brute"), value="brute"),
        ],
    ).ask()
    if attack is None:
        return None

    config = {
        "hash_str": hash_str.strip(), "algo": algo, "attack": attack,
        "hashcat": False, "keyspace": False, "quiet": False,
        "charset": "alphanum", "min_len": 1, "max_len": 6,
        "wordlist": DEFAULT_WORDLIST, "rules": None,
    }

    if attack == "dict":
        if _dict_options(q, config) is None:
            return None
    else:
        if _brute_options(q, config) is None:
            return None

    show_hc = q.confirm(t("prompt_hashcat"), default=False).ask()
    config["hashcat"] = bool(show_hc)

    quiet = q.confirm(t("prompt_quiet"), default=False).ask()
    config["quiet"] = bool(quiet)

    return config


# ---------------------------------------------------------------------------
# Flow: crack hash file
# ---------------------------------------------------------------------------

def _ask_file_config() -> dict | None:
    """Collect config for batch cracking from a file. Returns dict or None if cancelled."""
    q = _q()

    file_path = q.text(
        t("prompt_hash_file"),
        validate=lambda v: t("err_file_missing", v) if not Path(v).exists() else True,
    ).ask()
    if file_path is None:
        return None

    algo = q.select(t("prompt_algo"), choices=_algo_choices(q)).ask()
    if algo is None:
        return None

    attack = q.select(
        t("prompt_attack"),
        choices=[
            q.Choice(t("prompt_attack_dict"),  value="dict"),
            q.Choice(t("prompt_attack_brute"), value="brute"),
        ],
    ).ask()
    if attack is None:
        return None

    config = {
        "hash_file": file_path, "hash_str": None, "algo": algo,
        "attack": attack, "hashcat": False, "keyspace": False, "quiet": False,
        "charset": "alphanum", "min_len": 1, "max_len": 6,
        "wordlist": DEFAULT_WORDLIST, "rules": None,
    }

    if attack == "dict":
        if _dict_options(q, config) is None:
            return None
    else:
        if _brute_options(q, config) is None:
            return None

    quiet = q.confirm(t("prompt_quiet"), default=False).ask()
    config["quiet"] = bool(quiet)

    return config


# ---------------------------------------------------------------------------
# Flow: generate hashes from a password
# ---------------------------------------------------------------------------

def _generate_hash_flow() -> None:
    """Ask for a password, generate its hashes, optionally save to file."""
    q = _q()
    try:
        import bcrypt as _bcrypt
        HAS_BCRYPT = True
    except ImportError:
        HAS_BCRYPT = False

    from rich.table import Table
    from rich import box as rbox

    password = q.text(
        t("prompt_password"),
        validate=lambda v: t("err_empty_hash") if not v.strip() else True,
    ).ask()
    if password is None:
        return

    algo = q.select(
        t("prompt_algo"),
        choices=[
            q.Choice(t("prompt_algo_all"), value="all"),
            q.Choice("MD5",     value="md5"),
            q.Choice("SHA-1",   value="sha1"),
            q.Choice("SHA-256", value="sha256"),
            q.Choice("SHA-512", value="sha512"),
            q.Choice("bcrypt",  value="bcrypt"),
        ],
    ).ask()
    if algo is None:
        return

    pw = password.encode("utf-8")
    results = {}
    if algo in ("all", "md5"):
        results["MD5"] = hashlib.md5(pw).hexdigest()
    if algo in ("all", "sha1"):
        results["SHA-1"] = hashlib.sha1(pw).hexdigest()
    if algo in ("all", "sha256"):
        results["SHA-256"] = hashlib.sha256(pw).hexdigest()
    if algo in ("all", "sha512"):
        results["SHA-512"] = hashlib.sha512(pw).hexdigest()
    if algo in ("all", "bcrypt"):
        if HAS_BCRYPT:
            salt = _bcrypt.gensalt(rounds=12)
            results["bcrypt"] = _bcrypt.hashpw(pw, salt).decode()
        else:
            results["bcrypt"] = "[pip install bcrypt]"

    table = Table(
        title=f"Hashes for: [bold white]'{password}'[/]",
        box=rbox.ROUNDED,
    )
    table.add_column(t("col_algorithm"), style="cyan")
    table.add_column("Hash", style="yellow")
    for name, h in results.items():
        table.add_row(name, h)
    console.print(table)

    save_path = q.text(t("prompt_save_to_file"), default="").ask()
    if save_path and save_path.strip():
        with open(save_path.strip(), "a", encoding="utf-8") as f:
            for name, h in results.items():
                f.write(f"{name}:{h}:{password}\n")
        console.print(f"[dim]Saved -> {save_path.strip()}[/dim]")


# ---------------------------------------------------------------------------
# Flow: show hashcat commands without cracking
# ---------------------------------------------------------------------------

def _hashcat_cmds_flow() -> None:
    """Ask for a hash + algo, display equivalent hashcat commands."""
    q = _q()

    hash_str = q.text(
        t("prompt_hash"),
        validate=lambda v: t("err_empty_hash") if not v.strip() else True,
    ).ask()
    if hash_str is None:
        return
    hash_str = hash_str.strip()

    algo = q.select(t("prompt_algo"), choices=_algo_choices(q)).ask()
    if algo is None:
        return

    if algo == "auto":
        from hashers.identifier import identify
        candidates = identify(hash_str)
        algo = candidates[0] if candidates[0] != "Unknown" else "MD5"
        console.print(f"[dim]{t('auto_detected', algo)}[/dim]")

    wordlist_name = q.text(t("prompt_wordlist_name"), default="rockyou.txt").ask()
    if wordlist_name is None:
        wordlist_name = "rockyou.txt"

    print_hashcat_hint(hash_str, algo, wordlist_name.strip())


# ---------------------------------------------------------------------------
# Flow: standalone keyspace estimator
# ---------------------------------------------------------------------------

def _keyspace_flow() -> None:
    """Estimate brute force keyspace without running an attack."""
    q = _q()
    from attacks.brute_force import CHARSETS

    charset = q.select(t("prompt_charset"), choices=list(CHARSETS)).ask()
    if charset is None:
        return

    min_len = q.text(
        t("prompt_min_len"), default="1",
        validate=lambda v: t("err_invalid_number") if not v.isdigit() or int(v) < 1 else True,
    ).ask()
    if min_len is None:
        return

    max_len = q.text(
        t("prompt_max_len"), default="8",
        validate=lambda v: t("err_invalid_number") if not v.isdigit() or int(v) < 1 else True,
    ).ask()
    if max_len is None:
        return

    print_keyspace_estimate(charset, int(min_len), int(max_len))


# ---------------------------------------------------------------------------
# Flow: change UI language
# ---------------------------------------------------------------------------

def _change_lang_flow() -> None:
    """Switch the active UI language without restarting."""
    q = _q()

    lang = q.select(
        t("prompt_lang_select"),
        choices=[
            q.Choice("English", value="en"),
            q.Choice("Espanol", value="es"),
        ],
    ).ask()
    if lang is None:
        return

    set_lang(lang)
    msg = t("lang_changed_to_en") if lang == "en" else t("lang_changed_to_es")
    console.print(f"[bold green]{msg}[/]")


# ---------------------------------------------------------------------------
# Main interactive loop
# ---------------------------------------------------------------------------

def run_interactive() -> None:
    """Main menu loop — dispatches every available app feature."""
    q = _q()
    from crack import crack_single, demo_stuffing, resolve_algo

    while True:
        console.print()
        choice = q.select(
            t("menu_title"),
            choices=[
                q.Choice(t("menu_crack_hash"),   value="hash"),
                q.Choice(t("menu_crack_file"),   value="file"),
                q.Separator(),
                q.Choice(t("menu_gen_hash"),     value="gen_hash"),
                q.Choice(t("menu_hashcat_cmds"), value="hashcat_cmds"),
                q.Choice(t("menu_keyspace"),     value="keyspace"),
                q.Separator(),
                q.Choice(t("menu_stuffing"),     value="stuffing"),
                q.Choice(t("menu_algo_info"),    value="info"),
                q.Separator(),
                q.Choice(t("menu_change_lang"),  value="lang"),
                q.Choice(t("menu_exit"),         value="exit"),
            ],
        ).ask()

        if choice is None or choice == "exit":
            console.print(f"\n[bold]{t('interactive_goodbye')}[/]")
            break

        elif choice == "info":
            print_algo_table()

        elif choice == "stuffing":
            demo_stuffing()

        elif choice == "gen_hash":
            _generate_hash_flow()

        elif choice == "hashcat_cmds":
            _hashcat_cmds_flow()

        elif choice == "keyspace":
            _keyspace_flow()

        elif choice == "lang":
            _change_lang_flow()

        elif choice == "hash":
            config = _ask_hash_config()
            if config is None:
                console.print(f"[dim]{t('interactive_cancelled')}[/dim]")
                continue

            args = argparse.Namespace(**config)
            algo = resolve_algo(config["hash_str"], config["algo"])
            try:
                crack_single(config["hash_str"], algo, args)
            except Exception as e:
                console.print(f"[red]{t('err_generic', e)}[/]")

            again = q.confirm(t("prompt_another"), default=True).ask()
            if not again:
                console.print(f"\n[bold]{t('interactive_goodbye')}[/]")
                break

        elif choice == "file":
            config = _ask_file_config()
            if config is None:
                console.print(f"[dim]{t('interactive_cancelled')}[/dim]")
                continue

            path = Path(config["hash_file"])
            hashes = [
                line.strip() for line in path.read_text().splitlines()
                if line.strip() and not line.strip().startswith("#")
            ]
            console.print(f"\n[bold]{t('batch_cracking', len(hashes), path)}[/]\n")
            args = argparse.Namespace(**config)
            for i, h in enumerate(hashes, 1):
                console.print(f"\n[bold cyan]{t('hash_n_of_m', i, len(hashes))}[/] {h}")
                algo = resolve_algo(h, config["algo"])
                try:
                    crack_single(h, algo, args)
                except Exception as e:
                    console.print(f"[red]{t('err_generic', e)}[/]")
