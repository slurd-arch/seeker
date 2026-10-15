import json
import os
from datetime import datetime
from utils import GREEN, format_results_for_display

def create_output_dir():
    path = os.path.join(os.path.dirname(__file__), 'output')
    os.makedirs(path, exist_ok=True)
    return path

class OutputHandler:
    def __init__(self):
        self.output_dir = create_output_dir()
        self.timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    def save(self, results, query, query_type, formats=None):
        if formats is None:
            formats = ["txt"]
        safe_query = "".join(c for c in query if c.isalnum() or c in "-_.")[:30]
        saved = []
        if "txt" in formats:
            saved.append(self._save_txt(results, safe_query, query_type, query))
        if "json" in formats:
            saved.append(self._save_json(results, safe_query, query_type, query))
        if "html" in formats:
            saved.append(self._save_html(results, safe_query, query_type, query))
        return saved

    def _save_txt(self, results, safe_query, query_type, original_query):
        fname = f"osint_{query_type}_{safe_query}_{self.timestamp}.txt"
        fpath = os.path.join(self.output_dir, fname)
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(f"OSINT Report - {query_type}: {original_query}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n")
            f.write(format_results_for_display(results))
        print(GREEN + f"[+] TXT saved: output/{fname}")
        return fpath

    def _save_json(self, results, safe_query, query_type, original_query):
        fname = f"osint_{query_type}_{safe_query}_{self.timestamp}.json"
        fpath = os.path.join(self.output_dir, fname)
        data = {
            "query": original_query,
            "query_type": query_type,
            "generated": datetime.now().isoformat(),
            "results": [{"source": s, "data": d} for s, d in results]
        }
        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False, default=str)
        print(GREEN + f"[+] JSON saved: output/{fname}")
        return fpath

    def _save_html(self, results, safe_query, query_type, original_query):
        fname = f"osint_{query_type}_{safe_query}_{self.timestamp}.html"
        fpath = os.path.join(self.output_dir, fname)
        rows = ""
        for src, data in results:
            content = format_results_for_display([(src, data)]).replace("\n", "<br>").replace(" ", "&nbsp;")
            rows += f"<tr><td><strong>{src}</strong></td><td><pre>{content}</pre></td></tr>"

        html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>OSINT - {original_query}</title>
<style>
body{{background:#0d0d0d;color:#e0e0e0;font-family:'Segoe UI',sans-serif;padding:30px;}}
h1{{color:#ff4444;border-bottom:2px solid #ff4444;padding-bottom:10px;}}
table{{border-collapse:collapse;width:100%;margin-top:20px;}}
th,td{{border:1px solid #2a2a2a;padding:12px;text-align:left;vertical-align:top;}}
th{{background:#1a1a1a;color:#ff4444;}}
pre{{white-space:pre-wrap;font-size:12px;}}
</style></head><body>
<h1>📭 OSINT Report</h1>
<p>Query: <strong>{original_query}</strong> ({query_type})</p>
<p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
<table><tr><th>Source</th><th>Data</th></tr>{rows}</table>
</body></html>"""
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(html)
        print(GREEN + f"[+] HTML saved: output/{fname}")
        return fpath