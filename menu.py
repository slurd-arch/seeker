import sys
from utils import print_info, format_results_for_display, RED, YELLOW, CYAN, GREEN, Spinner, calculate_risk, print_risk_bar
from output_handler import OutputHandler
from validators import validate
from history import add_to_history, show_history, clear_history

MENU_OPTIONS = {
    "1": ("Email", "email"),
    "2": ("Username", "username"),
    "3": ("IP Address", "ip"),
    "4": ("Phone Number", "phone"),
    "5": ("Roblox Username", "username"),
    "6": ("Discord ID", "username"),
    "7": ("Minecraft Username", "username"),
    "8": ("Domain", "domain"),
}

def interactive_menu(lookup):
    while True:
        print("\n" + YELLOW + "=" * 50)
        print(CYAN + "  📭 Main Menu")
        print(YELLOW + "=" * 50)
        for k, (label, _) in MENU_OPTIONS.items():
            print(f"  [{k}] Search {label}")
        print("  [9] Bulk Search (from file)")
        print("  [10] View Search History")
        print("  [11] Clear History")
        print("  [0] Exit")
        print(YELLOW + "=" * 50)

        choice = input("  Select an option: ").strip()

        if choice == "0":
            print_info("Goodbye!")
            sys.exit(0)
        if choice == "9":
            bulk_search_menu(lookup)
            continue
        if choice == "10":
            show_history()
            continue
        if choice == "11":
            clear_history()
            continue
        if choice not in MENU_OPTIONS:
            print(RED + "  [!] Invalid choice.")
            continue

        label, query_type = MENU_OPTIONS[choice]
        query = input(f"  Enter {label}: ").strip()
        if not query:
            print(RED + "  [!] Empty input.")
            continue

        ok, result = validate(query, query_type)
        if not ok:
            print(RED + f"  [!] Invalid input: {result}")
            continue
        query = result

        print_info(f"Searching {label}: {query}")
        spinner = Spinner(f"Querying APIs for {query}")
        spinner.start()
        results = lookup.run_all_checks(query, query_type)
        spinner.stop()

        _handle_results(results, query, query_type)


def bulk_search_menu(lookup):
    filepath = input("  Enter path to targets file: ").strip()
    try:
        with open(filepath, 'r') as f:
            targets = [l.strip() for l in f if l.strip()]
    except FileNotFoundError:
        print(RED + "  [!] File not found.")
        return
    if not targets:
        print(RED + "  [!] File is empty.")
        return

    qt = input("  Query type (email/username/ip/phone/domain): ").strip().lower()
    if qt not in ["email", "username", "ip", "phone", "domain"]:
        print(RED + "  [!] Invalid type.")
        return

    print_info(f"Bulk searching {len(targets)} targets...")
    handler = OutputHandler()
    for i, target in enumerate(targets, 1):
        print(f"\n[{i}/{len(targets)}] {target}")
        ok, result = validate(target, qt)
        if not ok:
            print(RED + f"  [!] Skipping: {result}")
            continue
        results = lookup.run_all_checks(result, qt)
        add_to_history(result, qt, len(results))
        if results:
            handler.save(results, result, qt, ["txt", "json"])
    print_info("Bulk search complete.")


def _handle_results(results, query, query_type):
    add_to_history(query, query_type, len(results))

    if not results:
        print(RED + "\n[!] No data found.")
        return

    print("\n" + YELLOW + "=" * 60)
    print(CYAN + "📊 SUMMARY OF FINDINGS")
    print(YELLOW + "=" * 60)
    print(format_results_for_display(results))

    score, label, color = calculate_risk(results)
    print_risk_bar(score, label, color)

    print("\n  Save results?")
    print("  [1] TXT   [2] JSON   [3] HTML   [4] All   [5] Skip")
    sc = input("  Choice: ").strip()
    handler = OutputHandler()
    mapping = {"1": ["txt"], "2": ["json"], "3": ["html"], "4": ["txt", "json", "html"]}
    if sc in mapping:
        handler.save(results, query, query_type, mapping[sc])