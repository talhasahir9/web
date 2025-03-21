import requests
import time
import random
import threading
import pyautogui
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth

# Tier 1 Countries
TIER_1_COUNTRIES = ["US", "GB", "CA", "AU", "DE", "FR", "NL", "IT", "SE", "ES", "CH"]

# Free Proxy APIs
PROXY_APIS = [
    "https://proxylist.geonode.com/api/proxy-list?protocols=http,https&limit=50",
    "https://www.proxyscrape.com/api/v1/free-proxy-list?protocol=http",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://www.freeproxy.world/free-proxy/json",
    "https://proxyspace.pro/http.txt",
]

FAILED_PROXIES_FILE = "failed_proxies.txt"
URLS_FILE = "urls.txt"
BROWSER_LIFETIME = 10  # Restart browser after 10 visits

# Load URLs from file
def load_urls():
    try:
        with open(URLS_FILE, "r") as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"[!] Error: {URLS_FILE} not found!")
        return []

# Fetch & validate proxies
def get_free_proxies():
    all_proxies = set()
    for api in PROXY_APIS:
        try:
            response = requests.get(api, timeout=10)
            if response.status_code == 200:
                for line in response.text.split("\n"):
                    if line.strip():
                        all_proxies.add(f"http://{line.strip()}")
            print(f"[+] Fetched {len(all_proxies)} proxies from {api}")
        except Exception as e:
            print(f"[!] Error fetching proxies: {e}")
    return list(all_proxies)

def validate_proxy(proxy):
    try:
        response = requests.get("https://api64.ipify.org?format=json", proxies={"http": proxy, "https": proxy}, timeout=5)
        print(f"[+] Proxy {proxy} is working. IP: {response.json().get('ip', 'Unknown')}")
        return True
    except:
        return False

# Remove failed proxies & auto-refresh
def remove_failed_proxy(proxy, proxies):
    if proxy in proxies:
        proxies.remove(proxy)
        print(f"[🗑] Removed dead proxy: {proxy}")

def refresh_proxies():
    print("[🔄] Updating proxies...")
    return [proxy for proxy in get_free_proxies() if validate_proxy(proxy)]

# Apply stealth mode
def enable_stealth(page):
    stealth(page)
    print("[🕵] Stealth mode enabled!")

# Simulate human-like clicks
def human_like_click(page, element):
    box = element.bounding_box()
    if box:
        x, y = box["x"], box["y"]
        pyautogui.moveTo(x + random.randint(-5, 5), y + random.randint(-5, 5), duration=random.uniform(0.5, 1.5))
        element.click()
        print("[🖱] Human-like click performed")

# Scroll page randomly
def scroll_page(page):
    try:
        for _ in range(random.randint(3, 6)):  # Realistic scrolling
            time.sleep(random.uniform(2, 4))
            scroll_px = random.choice([100, 200, 300])
            page.evaluate(f"window.scrollBy(0, {scroll_px})")
        print("[+] Scrolling complete")
    except Exception as e:
        print(f"[!] Error while scrolling: {e}")

# Accept cookies
def accept_cookies(page):
    try:
        buttons = page.locator("button")
        for button in buttons.all():
            if any(word in button.inner_text().lower() for word in ["accept", "agree", "ok"]):
                human_like_click(page, button)
                print("[+] Accepted cookies")
                break
    except Exception as e:
        print(f"[!] Error accepting cookies: {e}")

# Close popups
def close_popups(page):
    try:
        popups = page.locator("button, .close, .dismiss")
        for popup in popups.all():
            if any(word in popup.inner_text().lower() for word in ["close", "dismiss", "×"]):
                human_like_click(page, popup)
                print("[+] Closed popup")
                break
    except Exception as e:
        print(f"[!] Error closing popups: {e}")

# Safe clicking (avoids ads & downloads)
def safe_clicks(page):
    try:
        links = page.locator("a")
        safe_links = [
            link for link in links.all() if link.get_attribute("href")
            and not any(x in link.inner_text().lower() for x in ["download", "ads", "sponsored"])
        ]
        if safe_links:
            for _ in range(random.randint(1, 3)):
                link = random.choice(safe_links)
                if link.is_visible():
                    human_like_click(page, link)
                    print("[+] Clicked a safe link")
                    time.sleep(random.uniform(3, 7))
                    scroll_page(page)
    except Exception as e:
        print(f"[!] Error during safe clicks: {e}")

# Multi-device browsing simulation
def get_random_device():
    devices = [
        {"browser": "Chrome", "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"},
        {"browser": "Safari", "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Safari/604.1.30"},
        {"browser": "Firefox", "user_agent": "Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/120.0"},
        {"browser": "Safari", "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_1) AppleWebKit/537.36 Mobile/15E148 Safari/537.36"},
        {"browser": "Chrome", "user_agent": "Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36"},
    ]
    return random.choice(devices)

# Visit URL using a proxy
def visit_url(url, proxies):
    global BROWSER_LIFETIME
    visit_count = 0

    while True:
        if not proxies:
            print("[⚠️] No working proxies left! Refreshing...")
            proxies.extend(refresh_proxies())

        proxy = proxies.pop(0)
        device = get_random_device()
        print(f"Using proxy: {proxy} with {device['browser']} for {url}")

        try:
            with sync_playwright() as p:
                browser_type = p.chromium if "Chrome" in device["browser"] else p.firefox if "Firefox" in device["browser"] else p.webkit
                browser = browser_type.launch(headless=False, proxy={"server": proxy})
                context = browser.new_context(user_agent=device["user_agent"])
                page = context.new_page()

                enable_stealth(page)

                print(f"Visiting: {url}")
                page.goto(url, timeout=90000)

                accept_cookies(page)
                close_popups(page)
                scroll_page(page)
                safe_clicks(page)

                time.sleep(random.uniform(90, 150))
                visit_count += 1

                if visit_count >= BROWSER_LIFETIME:
                    print("[🔄] Restarting browser to free memory...")
                    break

                browser.close()

        except Exception as e:
            print(f"[!] Error visiting {url}: {e}")
            remove_failed_proxy(proxy, proxies)
            time.sleep(5)