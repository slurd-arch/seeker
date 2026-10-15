import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils import print_info

# "status" = 200 means found. "text" = must contain marker. "not_found" = must NOT contain marker.
SITES = {
    "Instagram":       {"url": "https://www.instagram.com/{u}/", "method": "text", "marker": '"username"'},
    "Twitter/X":       {"url": "https://x.com/{u}", "method": "status"},
    "TikTok":          {"url": "https://www.tiktok.com/@{u}", "method": "text", "marker": "uniqueId"},
    "YouTube":         {"url": "https://www.youtube.com/@{u}", "method": "status"},
    "Reddit":          {"url": "https://www.reddit.com/user/{u}/about.json", "method": "text", "marker": '"name"'},
    "Twitch":          {"url": "https://www.twitch.tv/{u}", "method": "status"},
    "Pinterest":       {"url": "https://www.pinterest.com/{u}/", "method": "status"},
    "Tumblr":          {"url": "https://{u}.tumblr.com", "method": "status"},
    "Flickr":          {"url": "https://www.flickr.com/people/{u}", "method": "status"},
    "Vimeo":           {"url": "https://vimeo.com/{u}", "method": "status"},
    "SoundCloud":      {"url": "https://soundcloud.com/{u}", "method": "status"},
    "Spotify":         {"url": "https://open.spotify.com/user/{u}", "method": "status"},
    "Steam":           {"url": "https://steamcommunity.com/id/{u}", "method": "text", "marker": "profile_header"},
    "GitHub":          {"url": "https://api.github.com/users/{u}", "method": "status"},
    "GitLab":          {"url": "https://gitlab.com/api/v4/users?username={u}", "method": "text", "marker": '"username"'},
    "Bitbucket":       {"url": "https://bitbucket.org/{u}/", "method": "status"},
    "Dev.to":          {"url": "https://dev.to/{u}", "method": "status"},
    "Medium":          {"url": "https://medium.com/@{u}", "method": "status"},
    "HackerNews":      {"url": "https://news.ycombinator.com/user?id={u}", "method": "text", "marker": "karma"},
    "ProductHunt":     {"url": "https://www.producthunt.com/@{u}", "method": "status"},
    "Behance":         {"url": "https://www.behance.net/{u}", "method": "status"},
    "Dribbble":        {"url": "https://dribbble.com/{u}", "method": "status"},
    "ArtStation":      {"url": "https://www.artstation.com/{u}", "method": "status"},
    "DeviantArt":      {"url": "https://www.deviantart.com/{u}", "method": "status"},
    "Patreon":         {"url": "https://www.patreon.com/{u}", "method": "status"},
    "Ko-fi":           {"url": "https://ko-fi.com/{u}", "method": "status"},
    "BuyMeACoffee":    {"url": "https://www.buymeacoffee.com/{u}", "method": "status"},
    "Linktree":        {"url": "https://linktr.ee/{u}", "method": "status"},
    "About.me":        {"url": "https://about.me/{u}", "method": "status"},
    "Keybase":         {"url": "https://keybase.io/{u}", "method": "status"},
    "Telegram":        {"url": "https://t.me/{u}", "method": "text", "marker": "tgme_page_title"},
    "Roblox":          {"url": "https://www.roblox.com/users/profile?username={u}", "method": "status"},
    "Xbox":            {"url": "https://xboxgamertag.com/search/{u}", "method": "status"},
    "PlayStation":     {"url": "https://psnprofiles.com/{u}", "method": "status"},
    "Chess.com":       {"url": "https://api.chess.com/pub/player/{u}", "method": "status"},
    "Lichess":         {"url": "https://lichess.org/api/user/{u}", "method": "status"},
    "Duolingo":        {"url": "https://www.duolingo.com/2017-06-30/users?username={u}", "method": "text", "marker": '"username"'},
    "MyAnimeList":     {"url": "https://myanimelist.net/profile/{u}", "method": "status"},
    "AniList":         {"url": "https://anilist.co/user/{u}", "method": "status"},
    "Letterboxd":      {"url": "https://letterboxd.com/{u}/", "method": "status"},
    "Goodreads":       {"url": "https://www.goodreads.com/{u}", "method": "status"},
    "Last.fm":         {"url": "https://www.last.fm/user/{u}", "method": "status"},
    "Bandcamp":        {"url": "https://bandcamp.com/{u}", "method": "status"},
    "Mixcloud":        {"url": "https://www.mixcloud.com/{u}/", "method": "status"},
    "Replit":          {"url": "https://replit.com/@{u}", "method": "status"},
    "CodePen":         {"url": "https://codepen.io/{u}", "method": "status"},
    "HackerRank":      {"url": "https://www.hackerrank.com/{u}", "method": "status"},
    "LeetCode":        {"url": "https://leetcode.com/{u}", "method": "status"},
    "Kaggle":          {"url": "https://www.kaggle.com/{u}", "method": "status"},
    "StackOverflow":   {"url": "https://stackoverflow.com/users/filter?search={u}", "method": "status"},
    "Quora":           {"url": "https://www.quora.com/profile/{u}", "method": "status"},
    "Mastodon.social": {"url": "https://mastodon.social/@{u}", "method": "status"},
    "Bluesky":         {"url": "https://bsky.app/profile/{u}.bsky.social", "method": "status"},
    "VK":              {"url": "https://vk.com/{u}", "method": "status"},
    "OK.ru":           {"url": "https://ok.ru/{u}", "method": "status"},
    "Fiverr":          {"url": "https://www.fiverr.com/{u}", "method": "status"},
    "Freelancer":      {"url": "https://www.freelancer.com/u/{u}", "method": "status"},
    "Etsy":            {"url": "https://www.etsy.com/people/{u}", "method": "status"},
    "eBay":            {"url": "https://www.ebay.com/usr/{u}", "method": "status"},
    "Imgur":           {"url": "https://imgur.com/user/{u}", "method": "status"},
    "9GAG":            {"url": "https://9gag.com/u/{u}", "method": "status"},
    "Minds":           {"url": "https://www.minds.com/{u}/", "method": "status"},
    "Gab":             {"url": "https://gab.com/{u}", "method": "status"},
    "Rumble":          {"url": "https://rumble.com/user/{u}", "method": "status"},
    "Odysee":          {"url": "https://odysee.com/@{u}", "method": "status"},
    "Bitchute":        {"url": "https://www.bitchute.com/channel/{u}/", "method": "status"},
    "Snapchat":        {"url": "https://www.snapchat.com/add/{u}", "method": "status"},
    "Venmo":           {"url": "https://account.venmo.com/u/{u}", "method": "status"},
    "CashApp":         {"url": "https://cash.app/${u}", "method": "status"},
    "PayPal":          {"url": "https://www.paypal.com/paypalme/{u}", "method": "status"},
    "Discord.com":     {"url": "https://discord.com/users/{u}", "method": "status"},
    "Kik":             {"url": "https://ws2.kik.com/user/{u}", "method": "status"},
    "Periscope":       {"url": "https://www.periscope.tv/{u}", "method": "status"},
    "Blogspot":        {"url": "https://{u}.blogspot.com", "method": "status"},
    "Wordpress":       {"url": "https://{u}.wordpress.com", "method": "status"},
    "Weebly":          {"url": "https://{u}.weebly.com", "method": "status"},
    "Wix":             {"url": "https://{u}.wixsite.com", "method": "status"},
    "Wattpad":         {"url": "https://www.wattpad.com/user/{u}", "method": "status"},
    "TriviaCrack":     {"url": "https://api.preguntados.com/api/users/{u}/", "method": "status"},
    "Trello":          {"url": "https://trello.com/{u}", "method": "status"},
    "Asana":           {"url": "https://app.asana.com/-/login", "method": "status"},
    "Notion":          {"url": "https://{u}.notion.site", "method": "status"},
    "Myspace":         {"url": "https://myspace.com/{u}", "method": "status"},
    "RblxTrade":       {"url": "https://rblx.trade/p/{u}", "method": "status"},
    "NameMC":          {"url": "https://namemc.com/profile/{u}", "method": "status"},
    "MinecraftForums": {"url": "https://www.minecraftforum.net/members/{u}", "method": "status"},
    "PlanetMinecraft": {"url": "https://www.planetminecraft.com/member/{u}/", "method": "status"},
    "Hypixel":         {"url": "https://api.hypixel.net/player?name={u}", "method": "text", "marker": '"success":true'},
    "Speedrun.com":    {"url": "https://www.speedrun.com/api/v1/users?lookup={u}", "method": "text", "marker": '"data"'},
    "Chess24":         {"url": "https://chess24.com/en/profile/{u}", "method": "status"},
    "Itch.io":         {"url": "https://{u}.itch.io", "method": "status"},
    "Gumroad":         {"url": "https://{u}.gumroad.com", "method": "status"},
    "Substack":        {"url": "https://{u}.substack.com", "method": "status"},
    "HackerOne":       {"url": "https://hackerone.com/{u}", "method": "status"},
    "Bugcrowd":        {"url": "https://bugcrowd.com/{u}", "method": "status"},
    "Codewars":        {"url": "https://www.codewars.com/users/{u}", "method": "status"},
    "Exercism":        {"url": "https://exercism.org/profiles/{u}", "method": "status"},
}


class UsernameChecker:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/120.0.0.0 Safari/537.36"),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        })

    def _check_site(self, site_name, config, username):
        url = config["url"].format(u=username)
        method = config["method"]
        marker = config.get("marker", "")
        try:
            r = self.session.get(url, timeout=8, allow_redirects=True)
            if method == "status":
                if r.status_code == 200:
                    return {"site": site_name, "url": url, "method": "HTTP 200"}
            elif method == "text":
                if r.status_code == 200 and marker and marker in r.text:
                    return {"site": site_name, "url": url, "method": f"contains '{marker}'"}
        except Exception:
            return None
        return None

    def check_username(self, username):
        found = []
        print_info(f"Scanning {len(SITES)} platforms for '{username}'...")
        with ThreadPoolExecutor(max_workers=30) as executor:
            futures = {
                executor.submit(self._check_site, name, cfg, username): name
                for name, cfg in SITES.items()
            }
            for fut in as_completed(futures):
                try:
                    result = fut.result()
                    if result:
                        found.append(result)
                except Exception:
                    pass
        # Sort alphabetically by site for consistent output
        found.sort(key=lambda x: x["site"].lower())
        return found