import hashlib
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils import print_error, print_success, print_info
from username_checker import UsernameChecker

class OSINTLookup:
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        self.username_checker = UsernameChecker()

    def _key(self, name):
        k = self.config.get(name, "")
        return k if k and not k.startswith("YOUR_") else None

    def _request(self, method, url, max_retries=3, **kwargs):
        for attempt in range(max_retries):
            try:
                kwargs.setdefault("timeout", 15)
                res = (self.session.get(url, **kwargs) if method == "GET"
                       else self.session.post(url, **kwargs))
                if res.status_code == 429:
                    time.sleep(2 ** attempt)
                    continue
                if 500 <= res.status_code < 600 and attempt < max_retries - 1:
                    time.sleep(1.5)
                    continue
                return res
            except (requests.exceptions.Timeout, requests.exceptions.RequestException):
                if attempt < max_retries - 1:
                    time.sleep(1.5)
                else:
                    return None
        return None

    # ============================================================
    # FREE SOURCES
    # ============================================================

    def check_xposedornot(self, email):
        res = self._request("GET", f"https://api.xposedornot.com/v1/check-email/{email}")
        if res and res.status_code == 200:
            d = res.json()
            if d.get("breaches"):
                return "XposedOrNot", d
        return "XposedOrNot", None

    def check_hackmyip(self, ip):
        res = self._request("GET", f"https://hackmyip.com/api/v1/ip/{ip}")
        if res and res.status_code == 200:
            return "HackMyIP", res.json()
        return "HackMyIP", None

    def check_ipapi(self, ip):
        res = self._request("GET", f"http://ip-api.com/json/{ip}?fields=66846719")
        if res and res.status_code == 200:
            d = res.json()
            if d.get("status") == "success":
                return "IP-API", d
        return "IP-API", None

    def check_hudson_rock_email(self, email):
        res = self._request("GET",
            f"https://cavalier.hudsonrock.com/api/json/v2/osint-tools/search-by-email?email={email}")
        if res and res.status_code == 200:
            d = res.json()
            if d.get("message") or d.get("stealers") or d.get("data"):
                return "Hudson Rock", d
        return "Hudson Rock", None

    def check_hudson_rock_username(self, username):
        res = self._request("GET",
            f"https://cavalier.hudsonrock.com/api/json/v2/osint-tools/search-by-username?username={username}")
        if res and res.status_code == 200:
            d = res.json()
            if d.get("message") or d.get("stealers") or d.get("data"):
                return "Hudson Rock", d
        return "Hudson Rock", None

    def check_gravatar(self, email):
        h = hashlib.md5(email.strip().lower().encode()).hexdigest()
        res = self._request("GET", f"https://www.gravatar.com/{h}.json")
        if res and res.status_code == 200:
            return "Gravatar", res.json()
        return "Gravatar", None

    def check_emailrep(self, email):
        res = self._request("GET", f"https://emailrep.io/{email}")
        if res and res.status_code == 200:
            return "EmailRep", res.json()
        return "EmailRep", None

    def check_psbdmp(self, query):
        res = self._request("GET", f"https://psbdmp.ws/api/v3/search/{query}")
        if res and res.status_code == 200:
            d = res.json()
            if d.get("data"):
                return "psbdmp (Pastebin)", d
        return "psbdmp (Pastebin)", None

    def check_github(self, username):
        headers = {}
        token = self._key("github")
        if token:
            headers["Authorization"] = f"token {token}"
        res = self._request("GET", f"https://api.github.com/users/{username}", headers=headers)
        if res and res.status_code == 200:
            return "GitHub", res.json()
        return "GitHub", None

    def check_roblox(self, username):
        res = self._request("POST", "https://users.roblox.com/v1/usernames/users",
                            json={"usernames": [username], "excludeBannedUsers": False})
        if res and res.status_code == 200:
            d = res.json().get("data", [])
            if d:
                user = d[0]
                uid = user.get("id")
                info_res = self._request("GET", f"https://users.roblox.com/v1/users/{uid}")
                info = info_res.json() if info_res and info_res.status_code == 200 else {}
                # Also try to get friends count
                friends_res = self._request("GET", f"https://friends.roblox.com/v1/users/{uid}/friends/count")
                friends = friends_res.json() if friends_res and friends_res.status_code == 200 else {}
                return "Roblox", {
                    "id": uid,
                    "username": user.get("name"),
                    "display_name": user.get("displayName"),
                    "created": info.get("created"),
                    "description": info.get("description"),
                    "is_banned": info.get("isBanned"),
                    "has_verified_badge": info.get("hasVerifiedBadge"),
                    "friends_count": friends.get("count"),
                    "profile_url": f"https://www.roblox.com/users/{uid}/profile",
                }
        return "Roblox", None

    def check_minecraft(self, username):
        res = self._request("GET", f"https://api.mojang.com/users/profiles/minecraft/{username}")
        if res and res.status_code == 200:
            d = res.json()
            uuid = d.get("id")
            history_res = self._request("GET", f"https://api.mojang.com/user/profiles/{uuid}/names")
            history = history_res.json() if history_res and history_res.status_code == 200 else []
            return "Minecraft", {
                "username": d.get("name"),
                "uuid": uuid,
                "name_history": [h.get("name") for h in history],
            }
        return "Minecraft", None

    def check_discord(self, discord_id):
        res = self._request("GET", f"https://discordlookup.mesavirep.xyz/v1/user/{discord_id}")
        if res and res.status_code == 200:
            d = res.json()
            if d.get("id"):
                return "Discord", d
        return "Discord", None

    def check_dns(self, domain):
        results = {}
        for rtype in ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA"]:
            res = self._request("GET",
                f"https://cloudflare-dns.com/dns-query?name={domain}&type={rtype}",
                headers={"Accept": "application/dns-json"})
            if res and res.status_code == 200:
                answers = res.json().get("Answer", [])
                if answers:
                    results[rtype] = [a.get("data") for a in answers]
        if results:
            return "DNS Records", results
        return "DNS Records", None

    def _run_site_checker(self, username):
        found = self.username_checker.check_username(username)
        if found:
            return "Site Presence", found
        return "Site Presence", None

    # ============================================================
    # KEY-BASED SOURCES
    # ============================================================

    def check_ipinfo(self, ip):
        key = self._key("ipinfo")
        if not key:
            return "IPinfo", "API key missing"
        res = self._request("GET", f"https://ipinfo.io/{ip}/json?token={key}")
        if res and res.status_code == 200:
            return "IPinfo", res.json()
        return "IPinfo", None

    def check_hunterio(self, email):
        key = self._key("hunterio")
        if not key:
            return "Hunter.io", "API key missing"
        res = self._request("GET",
            f"https://api.hunter.io/v2/email-verifier?email={email}&api_key={key}")
        if res and res.status_code == 200:
            return "Hunter.io", res.json()
        return "Hunter.io", None

    def check_leakcheck(self, query):
        key = self._key("leakcheck")
        if not key:
            return "LeakCheck", "API key missing"
        res = self._request("GET", f"https://leakcheck.io/api/v2/query/{query}",
                            headers={"X-API-Key": key})
        if res and res.status_code == 200:
            d = res.json()
            if d.get("found"):
                return "LeakCheck", d
        return "LeakCheck", None

    def check_breachdirectory(self, query):
        key = self._key("breachdirectory")
        if not key:
            return "BreachDirectory", "API key missing"
        headers = {"X-RapidAPI-Key": key,
                   "X-RapidAPI-Host": "breachdirectory.p.rapidapi.com"}
        res = self._request("GET", "https://breachdirectory.p.rapidapi.com/",
                            headers=headers, params={"func": "auto", "term": query})
        if res and res.status_code == 200:
            d = res.json()
            if d.get("found"):
                return "BreachDirectory", d
        return "BreachDirectory", None

    def check_leaklookup(self, query, query_type):
        key = self._key("leaklookup")
        if not key:
            return "Leak-Lookup", "API key missing"
        res = self._request("POST", "https://leak-lookup.com/api/search",
                            data={"key": key, "type": query_type, "query": query})
        if res and res.status_code == 200:
            j = res.json()
            if j.get("error") == "false" and j.get("data"):
                return "Leak-Lookup", j
        return "Leak-Lookup", None

    # ============================================================
    # ORCHESTRATOR
    # ============================================================

    def run_all_checks(self, query, query_type):
        # Warn about missing keys
        missing = []
        for key_name, api in [("leakcheck", "LeakCheck"),
                              ("breachdirectory", "BreachDirectory"),
                              ("leaklookup", "Leak-Lookup")]:
            if not self._key(key_name):
                missing.append(api)
        if missing:
            print_error("Config", f"Missing API keys for: {', '.join(missing)} — edit conf.json")

        tasks = []

        if query_type == "email":
            tasks += [
                ("XposedOrNot", self.check_xposedornot, (query,)),
                ("Hunter.io", self.check_hunterio, (query,)),
                ("Hudson Rock", self.check_hudson_rock_email, (query,)),
                ("Gravatar", self.check_gravatar, (query,)),
                ("EmailRep", self.check_emailrep, (query,)),
                ("GitHub", self.check_github, (query,)),
            ]

        if query_type == "username":
            tasks += [
                ("GitHub", self.check_github, (query,)),
                ("Hudson Rock", self.check_hudson_rock_username, (query,)),
                ("Roblox", self.check_roblox, (query,)),
                ("Minecraft", self.check_minecraft, (query,)),
                ("Discord", self.check_discord, (query,)),
                ("Site Presence", self._run_site_checker, (query,)),
            ]

        if query_type == "ip":
            tasks += [
                ("HackMyIP", self.check_hackmyip, (query,)),
                ("IP-API", self.check_ipapi, (query,)),
                ("IPinfo", self.check_ipinfo, (query,)),
            ]

        if query_type == "domain":
            tasks += [("DNS Records", self.check_dns, (query,))]

        if query_type in ["email", "username"]:
            tasks.append(("psbdmp (Pastebin)", self.check_psbdmp, (query,)))

        tasks.append(("LeakCheck", self.check_leakcheck, (query,)))
        tasks.append(("BreachDirectory", self.check_breachdirectory, (query,)))
        if query_type in ["email", "username", "phone", "ip"]:
            tasks.append(("Leak-Lookup", self.check_leaklookup, (query, query_type)))

        results = []
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {executor.submit(fn, *args): name for name, fn, args in tasks}
            for fut in as_completed(futures):
                name = futures[fut]
                try:
                    src, data = fut.result()
                    if isinstance(data, str) and "missing" in data.lower():
                        print_error(src, data)
                    elif data:
                        results.append((src, data))
                        print_success(src, "Data found")
                    else:
                        print_info(f"{src}: no data")
                except Exception as e:
                    print_error(name, f"Error: {e}")
        return results