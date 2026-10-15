import json
import os
import sys
import threading
import time
from colorama import Fore, Style, init

init(autoreset=True)

RED = Fore.LIGHTRED_EX
WHITE = Fore.WHITE
YELLOW = Fore.YELLOW
GREEN = Fore.GREEN
CYAN = Fore.CYAN
MAGENTA = Fore.MAGENTA
DIM = Style.DIM

ASCII_ART = r"""
  _____           __            
 / ___/___  ___  / /_____  _____
 \__ \/ _ \/ _ \/ //_/ _ \/ ___/
 ___/ /  __/  __/ ,< /  __/ /    
/____/\___/\___/_/|_|\___/_/

     ~: 📭 Multi OSINT Tool :~
        => Made by @Slurd
"""


def print_banner():
    lines = ASCII_ART.strip('\n').split('\n')
    total = len(lines)
    for i, line in enumerate(lines):
        progress = i / (total - 1) if total > 1 else 0
        r, g, b = 255, int(255 * progress), int(255 * progress)
        print(f"\033[38;2;{r};{g};{b}m{line}")
    print(Style.RESET_ALL + YELLOW + "=" * 60)


def print_tagline():
    print("Search inputs through countless databreaches, dataleaks, and stealerlogs\n")


def load_config():
    path = os.path.join(os.path.dirname(__file__), 'conf.json')
    if not os.path.exists(path):
        print(RED + "[!] conf.json not found.")
        return {}
    with open(path, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            print(RED + "[!] Invalid JSON in conf.json.")
            return {}


def print_error(source, message):
    print(RED + f"[-] {source}: {message}")


def print_success(source, message):
    print(GREEN + f"[+] {source}: {message}")


def print_info(message):
    print(CYAN + f"[*] {message}")


class Spinner:
    FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def __init__(self, message="Searching"):
        self.message = message
        self._stop = threading.Event()
        self._thread = None

    def _spin(self):
        i = 0
        while not self._stop.is_set():
            frame = self.FRAMES[i % len(self.FRAMES)]
            sys.stdout.write(f"\r{CYAN}{frame} {self.message}...{Style.RESET_ALL}")
            sys.stdout.flush()
            time.sleep(0.08)
            i += 1

    def start(self):
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop.set()
        if self._thread:
            self._thread.join()
        sys.stdout.write("\r" + " " * (len(self.message) + 20) + "\r")
        sys.stdout.flush()


def calculate_risk(results):
    if not results:
        return 0, "CLEAN", GREEN

    score = 0
    critical_sources = ["LeakCheck", "BreachDirectory", "Leak-Lookup", "Hudson Rock",
                        "XposedOrNot", "ProxyNova", "IntelligenceX", "psbdmp", "HIBP"]

    for source, data in results:
        if any(c in source for c in critical_sources):
            score += 25
        elif source in ["IPinfo", "HackMyIP", "IP-API"]:
            score += 5
        elif source == "GitHub":
            score += 5
        elif source == "Hunter.io":
            score += 10
        elif source in ["Roblox", "Minecraft", "Discord"]:
            score += 8
        elif source == "Site Presence":
            score += 3

    score = min(score, 100)

    if score >= 75:
        return score, "CRITICAL", RED
    elif score >= 50:
        return score, "HIGH", RED
    elif score >= 25:
        return score, "MEDIUM", YELLOW
    elif score > 0:
        return score, "LOW", YELLOW
    return score, "CLEAN", GREEN


def print_risk_bar(score, label, color):
    filled = int(score / 100 * 30)
    bar = "█" * filled + "░" * (30 - filled)
    print(f"\n{color}  Risk Score: [{bar}] {score}/100  →  {label}{Style.RESET_ALL}\n")


def _format_value(value, indent=4):
    pad = " " * indent
    if isinstance(value, dict):
        lines = []
        for k, v in value.items():
            if v in (None, "", [], {}):
                continue
            if isinstance(v, (dict, list)):
                lines.append(f"{pad}{k}:")
                lines.append(_format_value(v, indent + 2))
            else:
                lines.append(f"{pad}{k}: {v}")
        return "\n".join(lines) if lines else f"{pad}(empty)"
    elif isinstance(value, list):
        if not value:
            return f"{pad}(empty)"
        if all(not isinstance(x, (dict, list)) for x in value):
            return "\n".join(f"{pad}- {x}" for x in value)
        lines = []
        for i, item in enumerate(value, 1):
            lines.append(f"{pad}[{i}]")
            lines.append(_format_value(item, indent + 2))
        return "\n".join(lines)
    else:
        return f"{pad}{value}"


def format_results_for_display(results):
    if not results:
        return "[-] No data found."
    out = ""
    for source, data in results:
        out += f"\n{'='*60}\n[+] Source: {source}\n{'='*60}\n"
        out += _format_value(data, indent=2)
        out += "\n"
    return out