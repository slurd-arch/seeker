import json
import os
from datetime import datetime
from utils import CYAN, GREEN, YELLOW

HISTORY_FILE = os.path.join(os.path.dirname(__file__), 'output', 'history.json')


def _ensure_dir():
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def add_to_history(query, query_type, num_results):
    history = load_history()
    history.append({
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "query": query,
        "type": query_type,
        "results_count": num_results,
    })
    _ensure_dir()
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2)


def show_history(limit=25):
    history = load_history()
    if not history:
        print(YELLOW + "\n📜 No search history yet.")
        return
    print(CYAN + f"\n📜 Last {min(limit, len(history))} Searches:")
    print(YELLOW + "-" * 70)
    for entry in history[-limit:]:
        ts = entry['timestamp'].replace('T', ' ')[:19]
        print(f"  {GREEN}[{ts}]{CYAN} {entry['type']:10s} → {entry['query']} ({entry['results_count']} results)")
    print(YELLOW + "-" * 70)


def clear_history():
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
    print(GREEN + "[+] History cleared.")