import json
import os
from datetime import datetime
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Your exact ASCII art. Using r""" to safely handle the backslashes
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
    """Print the ASCII art with a smooth red-to-white vertical gradient."""
    lines = ASCII_ART.strip('\n').split('\n')
    total_lines = len(lines)
    
    for i, line in enumerate(lines):
        # Calculate gradient progress from 0.0 (top) to 1.0 (bottom)
        progress = i / (total_lines - 1) if total_lines > 1 else 0
        
        # Interpolate from Red (255, 0, 0) to White (255, 255, 255)
        r = 255
        g = int(255 * progress)
        b = int(255 * progress)
        
        # ANSI TrueColor escape code
        color_code = f"\033[38;2;{r};{g};{b}m"
        
        print(f"{color_code}{line}")
        
    # Reset the color back to normal after the art
    print(Style.RESET_ALL + Fore.YELLOW + "=" * 60)

def print_tagline():
    """Print the tagline in normal terminal color."""
    print("Search inputs through countless databreaches, dataleaks, and stealerlogs\n")

def load_config():
    """Load API keys from conf.json."""
    config_path = os.path.join(os.path.dirname(__file__), 'conf.json')
    if not os.path.exists(config_path):
        print(Fore.RED + "[!] conf.json not found. Please create it with your API keys.")
        return {}
    
    with open(config_path, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            print(Fore.RED + "[!] Invalid JSON in conf.json.")
            return {}

def create_output_dir():
    """Create the output directory if it doesn't exist."""
    output_dir = os.path.join(os.path.dirname(__file__), 'output')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir

def save_to_file(formatted_results, query, query_type):
    """Save formatted results to a dated txt file in the output folder."""
    output_dir = create_output_dir()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"osint_report_{query_type}_{timestamp}.txt"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"OSINT Report for {query_type}: {query}\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")
        f.write(formatted_results)
        
    print(Fore.GREEN + f"\n[+] Report saved successfully to: output/{filename}")

def format_results_for_display(results):
    """Format the raw API results into a clean, readable string."""
    if not results:
        return "[-] No data found."
        
    formatted = ""
    for source, data in results:
        formatted += f"[+] Source: {source}\n"
        formatted += "-" * 50 + "\n"
        
        if isinstance(data, list):
            for i, item in enumerate(data, 1):
                formatted += f"  Record {i}:\n"
                if isinstance(item, dict):
                    for key, value in item.items():
                        if value:
                            formatted += f"    {key}: {value}\n"
                else:
                    formatted += f"    {item}\n"
        elif isinstance(data, dict):
            for key, value in data.items():
                if value:
                    formatted += f"  {key}: {value}\n"
        else:
            formatted += f"  {data}\n"
            
        formatted += "-" * 50 + "\n\n"
        
    return formatted

def print_error(source, message):
    """Print errors cleanly in red."""
    print(Fore.RED + f"[-] {source}: {message}")
