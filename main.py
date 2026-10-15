import argparse
import sys
from colorama import Fore
from utils import (load_config, print_banner, print_tagline, format_results_for_display,
                   print_info, Spinner, calculate_risk, print_risk_bar)
from apis import OSINTLookup
from output_handler import OutputHandler
from validators import validate
from history import add_to_history
from help import HELP_TEXT


def main():
    print_banner()

    if len(sys.argv) == 1:
        print_tagline()
        config = load_config()
        lookup = OSINTLookup(config)
        from menu import interactive_menu
        interactive_menu(lookup)
        return

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-h", "--help", action="store_true")
    parser.add_argument("-e", "--email", type=str)
    parser.add_argument("-u", "--username", type=str)
    parser.add_argument("-p", "--phone", type=str)
    parser.add_argument("-i", "--ip", type=str)
    parser.add_argument("-r", "--roblox", type=str)
    parser.add_argument("-d", "--discord", type=str)
    parser.add_argument("-m", "--minecraft", type=str)
    parser.add_argument("-D", "--domain", type=str)
    parser.add_argument("-b", "--bulk", type=str)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--html", action="store_true")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    if args.help:
        print(HELP_TEXT)
        sys.exit(0)

    config = load_config()
    lookup = OSINTLookup(config)

    formats = ["txt"]
    if args.all:
        formats = ["txt", "json", "html"]
    elif args.json:
        formats = ["json"]
    elif args.html:
        formats = ["html"]

    if args.bulk:
        qt = "email"
        if args.username: qt = "username"
        elif args.ip: qt = "ip"
        elif args.phone: qt = "phone"
        elif args.domain: qt = "domain"
        _bulk(lookup, args.bulk, qt, formats)
        return

    query, qt, label = "", "", ""
    if args.email: query, qt, label = args.email, "email", "Email"
    elif args.username: query, qt, label = args.username, "username", "Username"
    elif args.phone: query, qt, label = args.phone, "phone", "Phone"
    elif args.ip: query, qt, label = args.ip, "ip", "IP"
    elif args.roblox: query, qt, label = args.roblox, "username", "Roblox"
    elif args.discord: query, qt, label = args.discord, "username", "Discord"
    elif args.minecraft: query, qt, label = args.minecraft, "username", "Minecraft"
    elif args.domain: query, qt, label = args.domain, "domain", "Domain"
    else:
        print(Fore.RED + "[!] No valid query. Use -h.")
        sys.exit(1)

    ok, result = validate(query, qt)
    if not ok:
        print(Fore.RED + f"[!] Invalid input: {result}")
        sys.exit(1)
    query = result

    print_info(f"Searching {label}: {query}")
    spinner = Spinner(f"Querying APIs for {query}")
    spinner.start()
    results = lookup.run_all_checks(query, qt)
    spinner.stop()

    add_to_history(query, qt, len(results))
    _output(results, query, qt, formats)


def _bulk(lookup, filepath, qt, formats):
    try:
        with open(filepath) as f:
            targets = [l.strip() for l in f if l.strip()]
    except FileNotFoundError:
        print(Fore.RED + f"[!] File not found: {filepath}")
        return
    if not targets:
        print(Fore.RED + "[!] File is empty.")
        return

    print_info(f"Bulk searching {len(targets)} targets...")
    handler = OutputHandler()
    for i, t in enumerate(targets, 1):
        print(f"\n{'='*60}\n[{i}/{len(targets)}] {t}\n{'='*60}")
        ok, result = validate(t, qt)
        if not ok:
            print(Fore.RED + f"[!] Skipping: {result}")
            continue
        results = lookup.run_all_checks(result, qt)
        add_to_history(result, qt, len(results))
        if results:
            print(format_results_for_display(results))
            handler.save(results, result, qt, formats)
    print_info("Bulk search complete.")


def _output(results, query, qt, formats):
    if not results:
        print(Fore.RED + "\n[!] No data found.")
        return
    print("\n" + Fore.YELLOW + "=" * 60)
    print(Fore.CYAN + "📊 SUMMARY OF FINDINGS")
    print(Fore.YELLOW + "=" * 60)
    print(format_results_for_display(results))

    score, label, color = calculate_risk(results)
    print_risk_bar(score, label, color)

    OutputHandler().save(results, query, qt, formats)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Cancelled.")
        sys.exit(0)