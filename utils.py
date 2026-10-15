def _format_value(value, indent=4):
    """Recursively format any value (dict, list, str) with proper indentation."""
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
        return "\n".join(lines)
    elif isinstance(value, list):
        if not value:
            return f"{pad}(empty)"
        # If it's a list of simple values
        if all(not isinstance(x, (dict, list)) for x in value):
            return "\n".join(f"{pad}- {x}" for x in value)
        # List of dicts
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