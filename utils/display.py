from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from hashers.algorithms import ALGO_INFO
from utils.lang import t

console = Console()

BANNER = (
    "\n"
    "  +--------------------------------------------------+\n"
    "  |   ____  ____      _      ____  _  __            |\n"
    "  |  / ___||  _ \\    / \\    / ___|| |/ /            |\n"
    "  | | |    | |_) |  / _ \\  | |    | ' /             |\n"
    "  | | |___ |  _ <  / ___ \\ | |___ | . \\             |\n"
    "  |  \\____||_| \\_\\/_/   \\_\\ \\____||_|\\_\\            |\n"
    "  |                                                 |\n"
    "  |  >>  Password Hash Cracker        v1.0  <<      |\n"
    "  |  >>  Dictionary | BruteForce | Stuffing  <<     |\n"
    "  +--------------------------------------------------+\n"
)


def print_banner():
    console.print(Text(BANNER, style="bold red"))
    console.print(f"[dim]{t('disclaimer')}[/dim]\n")


def print_algo_table():
    table = Table(
        title=f"[bold cyan]{t('info_title')}[/]",
        box=box.ROUNDED,
        border_style="cyan",
        show_lines=True,
    )
    table.add_column(t("col_algorithm"), style="bold yellow", no_wrap=True)
    table.add_column(t("col_bits"), justify="right", style="dim")
    table.add_column(t("col_year"), justify="right", style="dim")
    table.add_column(t("col_broken"), justify="center")
    table.add_column(t("col_hashcat_mode"), justify="center", style="dim")
    table.add_column(t("col_notes"), max_width=55)

    for name, info in ALGO_INFO.items():
        broken = f"[bold red]{t('yes')}[/]" if info["broken"] else f"[bold green]{t('no')}[/]"
        mode = str(info.get("hashcat_mode", "-"))
        note = t(f"algo_note_{name}")
        table.add_row(name, str(info["bits"]), str(info["year"]), broken, mode, note)

    console.print(table)


def print_result(cracked, algorithm: str, attempts: int, elapsed: float, attack_type: str = ""):
    speed = attempts / elapsed if elapsed > 0 else 0
    tag = f" [{attack_type}]" if attack_type else ""

    if cracked:
        console.print(Panel(
            f"[bold green]{t('cracked_msg')}[/]{tag}\n\n"
            f"  {t('label_plaintext'):<12}: [bold white]{cracked}[/]\n"
            f"  {t('label_algorithm'):<12}: {algorithm}\n"
            f"  {t('label_attempts'):<12}: {attempts:,}\n"
            f"  {t('label_time'):<12}: {elapsed:.3f}s\n"
            f"  {t('label_speed'):<12}: {speed:,.0f} H/s",
            title=f"[bold green]{t('cracked_title')}[/]",
            border_style="green",
        ))
    else:
        console.print(Panel(
            f"[bold red]{t('not_found_msg')}[/]{tag}\n\n"
            f"  {t('label_algorithm'):<12}: {algorithm}\n"
            f"  {t('label_attempts'):<12}: {attempts:,}\n"
            f"  {t('label_time'):<12}: {elapsed:.3f}s\n"
            f"  {t('label_speed'):<12}: {speed:,.0f} H/s",
            title=f"[bold red]{t('failed_title')}[/]",
            border_style="red",
        ))


def print_hashcat_hint(target_hash: str, algorithm: str, wordlist: str = "rockyou.txt"):
    from hashers.algorithms import normalize_algo
    algo = normalize_algo(algorithm)
    mode = ALGO_INFO.get(algo, {}).get("hashcat_mode", "?")
    console.print(Panel(
        f"[bold cyan]{t('hashcat_dict')}[/]\n"
        f"hashcat -m {mode} -a 0 '{target_hash}' {wordlist}\n\n"
        f"[bold cyan]{t('hashcat_rules')}[/]\n"
        f"hashcat -m {mode} -a 0 '{target_hash}' {wordlist} -r rules/best64.rule\n\n"
        f"[bold cyan]{t('hashcat_brute')}[/]\n"
        f"hashcat -m {mode} -a 3 '{target_hash}' ?a?a?a?a?a?a?a?a\n\n"
        f"[dim]{t('hashcat_gpu_note')}[/dim]",
        title=f"[cyan]{t('hashcat_title')}[/]",
        border_style="cyan",
    ))


def print_keyspace_estimate(charset: str, min_len: int, max_len: int, speed: int = 1_000_000):
    from attacks.brute_force import estimate_keyspace, CHARSETS
    chars = CHARSETS.get(charset, charset)
    total = estimate_keyspace(charset, min_len, max_len)
    eta_s = total / speed if speed > 0 else float("inf")

    table = Table(title=t("keyspace_title"), box=box.SIMPLE)
    table.add_column(t("keyspace_charset").split()[0])
    table.add_column("Value", style="yellow")
    table.add_row(t("keyspace_charset"), f"{charset} ({len(chars)} chars)")
    table.add_row(t("keyspace_range"), f"{min_len}-{max_len}")
    table.add_row(t("keyspace_total"), f"{total:,}")
    table.add_row(t("keyspace_eta"), f"{eta_s:,.1f}s ({eta_s/3600:.2f}h)")
    console.print(table)


def print_stuffing_results(hits: list, total: int):
    if hits:
        console.print(f"\n[bold red]{t('stuffing_compromised', len(hits), total)}[/]\n")
        table = Table(box=box.SIMPLE, border_style="red")
        table.add_column(t("col_username"), style="yellow")
        table.add_column(t("col_reused_pw"), style="red")
        for username, password in hits:
            table.add_row(username, password)
        console.print(table)
    else:
        console.print(f"[bold green]{t('stuffing_none')}[/]")


def print_defenses(strategies: list):
    table = Table(
        title=f"[bold cyan]{t('defense_title')}[/]",
        box=box.ROUNDED,
        border_style="blue",
        show_lines=True,
    )
    table.add_column(t("col_strategy"), style="bold yellow", max_width=30)
    table.add_column(t("col_impact"), justify="center")
    table.add_column(t("col_details"), max_width=60)

    for i, s in enumerate(strategies):
        impact_key = f"impact_{s['impact']}"
        impact_label = t(impact_key)
        impact_color = (
            "red" if s["impact"] == "Critical" else
            "yellow" if s["impact"] == "High" else "green"
        )
        name = t(f"defense_{i}_name")
        detail = t(f"defense_{i}_detail")
        table.add_row(name, f"[{impact_color}]{impact_label}[/]", detail)

    console.print(table)
