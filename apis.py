import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils import print_error, format_results_for_display

class OSINTLookup:
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def check_xposedornot(self, email):
        url = f"https://api.xposedornot.com/v1/check-email/{email}"
        try:
            res = self.session.get(url, timeout=10)
            if res.status_code == 200:
                data = res.json()
                if "breaches" in data and data["breaches"]:
                    return "XposedOrNot", data["breaches"]
            return "XposedOrNot", None
        except Exception as e:
            return "XposedOrNot", f"Error: {str(e)}"

    def check_hackmyip(self, ip):
        url = f"https://hackmyip.com/api/v1/ip/{ip}"
        try:
            res = self.session.get(url, timeout=10)
            if res.status_code == 200:
                return "HackMyIP", res.json()
            return "HackMyIP", None
        except Exception as e:
            return "HackMyIP", f"Error: {str(e)}"

    def check_leakcheck(self, query):
        key = self.config.get("leakcheck")
        if not key or key == "YOUR_LEAKCHECK_API_KEY":
            return "LeakCheck", "API key missing in conf.json"
        
        url = f"https://leakcheck.io/api/v2/query/{query}"
        headers = {"X-API-Key": key}
        try:
            res = self.session.get(url, headers=headers, timeout=15)
            if res.status_code == 200:
                data = res.json()
                if data.get("found"):
                    return "LeakCheck", data.get("result", [])
            return "LeakCheck", None
        except Exception as e:
            return "LeakCheck", f"Error: {str(e)}"

    def check_breachdirectory(self, query):
        key = self.config.get("breachdirectory")
        if not key or key == "YOUR_RAPIDAPI_KEY":
            return "BreachDirectory", "API key missing in conf.json"
        
        url = "https://breachdirectory.p.rapidapi.com/"
        headers = {
            "X-RapidAPI-Key": key,
            "X-RapidAPI-Host": "breachdirectory.p.rapidapi.com"
        }
        params = {"func": "auto", "term": query}
        try:
            res = self.session.get(url, headers=headers, params=params, timeout=15)
            if res.status_code == 200:
                data = res.json()
                if data.get("found"):
                    return "BreachDirectory", data.get("result", [])
            return "BreachDirectory", None
        except Exception as e:
            return "BreachDirectory", f"Error: {str(e)}"

    def check_leaklookup(self, query, query_type):
        key = self.config.get("leaklookup")
        if not key or key == "YOUR_LEAKLOOKUP_API_KEY":
            return "Leak-Lookup", "API key missing in conf.json"
        
        url = "https://leak-lookup.com/api/search"
        data = {"key": key, "type": query_type, "query": query}
        try:
            res = self.session.post(url, data=data, timeout=15)
            if res.status_code == 200:
                json_data = res.json()
                if json_data.get("error") == "false" and json_data.get("data"):
                    return "Leak-Lookup", json_data.get("data")
            return "Leak-Lookup", None
        except Exception as e:
            return "Leak-Lookup", f"Error: {str(e)}"

    def run_all_checks(self, query, query_type):
        tasks = []
        
        if query_type == "email":
            tasks.append(("XposedOrNot", self.check_xposedornot, (query,)))
        
        if query_type == "ip":
            tasks.append(("HackMyIP", self.check_hackmyip, (query,)))
            tasks.append(("Leak-Lookup", self.check_leaklookup, (query, "ip")))
        
        tasks.append(("LeakCheck", self.check_leakcheck, (query,)))
        tasks.append(("BreachDirectory", self.check_breachdirectory, (query,)))
        
        if query_type in ["email", "username", "phone"]:
            tasks.append(("Leak-Lookup", self.check_leaklookup, (query, query_type)))

        results = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_source = {
                executor.submit(func, *args): source 
                for source, func, args in tasks
            }
            
            for future in as_completed(future_to_source):
                source = future_to_source[future]
                try:
                    src_name, data = future.result()
                    if data:
                        results.append((src_name, data))
                    else:
                        print_error(src_name, "No data found.")
                except Exception as e:
                    print_error(source, f"Unexpected error: {str(e)}")
        
        return results