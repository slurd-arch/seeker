import argparse
import sys
from colorama import Fore
from utils import load_config, print_banner, print_tagline, format_results_for_display, save_to_file
from apis import OSINTLookup
from help import HELP_TEXT

def main():
    # 1. Always print the banner first
    print_banner()

    # 2. Setup argument parser with short flags
    parser = argparse.ArgumentParser(
        description="Multi OSINT Tool - Breach & Data Lookup",
        add_help=False
    )
    
    parser.add_argument("-h", "--help", action="store_true", help="Show this help message")
    parser.add_argument("-e", "--email", type=str, help="Search by Email address")
    parser.add_argument("-u", "--username", type=str, help="Search by Username")
    parser.add_argument("-p", "--phone", type=str, help="Search by Phone Number")
    parser.add_argument("-i", "--ip", type=str, help="Search by IP Address")
    parser.add_argument("-r", "--roblox", type=str, help="Search by Roblox Username")
    parser.add_argument("-d", "--discord", type=str, help="Search by Discord Username/ID")
    parser.add_argument("-m", "--minecraft", type=str, help="Search by Minecraft Username")

    args = parser.parse_args()

    # 3. Handle `python main.py` (No arguments)
    if len(sys.argv) == 1:
        print_tagline()
        sys.exit(0)

    # 4. Handle `python main.py -h` (Help flag)
    if args.help:
        print(HELP_TEXT)
        sys.exit(0)

    # 5. Handle search queries
    query = ""
    query_type = ""
    
    if args.email:
        query, query_type = args.email, "email"
    elif args.username:
        query, query_type = args.username, "username"
    elif args.phone:
        query, query_type = args.phone, "phone"
    elif args.ip:
        query, query_type = args.ip, "ip"
    elif args.roblox:
        query, query_type = args.roblox, "username"
        print(f"[*] Querying Roblox: {query}")
    elif args.discord:
        query, query_type = args.discord, "username"
        print(f"[*] Querying Discord: {query}")
    elif args.minecraft:
        query, query_type = args.minecraft, "username"
        print(f"[*] Querying Minecraft: {query}")
    else:
        print(Fore.RED + "[!] No valid query provided. Use -h for help.")
        sys.exit(1)

    # 6. Run the OSINT checks
    config = load_config()
    if not config:
        print("[!] Warning: No API keys loaded. Only keyless APIs will work.")

    lookup = OSINTLookup(config)

    print(f"[*] Searching breach databases for: {query} (Type: {query_type})\n")

    raw_results = lookup.run_all_checks(query, query_type)

    # 7. Display and save results
    if raw_results:
        formatted_output = format_results_for_display(raw_results)
        
        print("\n" + "=" * 60)
        print("📊 SUMMARY OF FINDINGS")
        print("=" * 60)
        print(formatted_output)
        
        save_to_file(formatted_output, query, query_type)
    else:
        print("\n[!] No data found across any checked APIs.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Operation cancelled by user.")
        sys.exit(0)