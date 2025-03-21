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
            urls = [line.strip() for line in file if line.strip()]
            if not urls:
                print("[❌] No URLs found in urls.txt. Please add at least one URL!")
                exit()
            return urls
    except FileNotFoundError:
        print(f"[❌] Error: {URLS_FILE} not found! Create the file and add URLs.")
        exit()

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
            print(f"[✅] Fetched {len(all_proxies)} proxies from {api}")
        except Exception as e:
            print(f"[❌] Error fetching proxies: {e}")
    if not all_proxies:
        print("[❌] No proxies available. Exiting...")
        exit()
    return list(all_proxies)

def validate_proxy(proxy):
    try:
        response = requests.get("https://api64.ipify.org?format=json", proxies={"http": proxy, "https": proxy}, timeout=5)
        print(f"[✅] Proxy {proxy} is working. IP: {response.json().get('ip', 'Unknown')}")
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
    proxies = [proxy for proxy in get_free_proxies() if validate_proxy(proxy)]
    if not proxies:
        print("[❌] No working proxies available. Exiting...")
        exit()
    return proxies

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
        print("[📜] Scrolling complete")
    except Exception as e:
        print(f"[❌] Error while scrolling: {e}")

# Accept cookies
def accept_cookies(page):
    try:
        buttons = page.locator("button")
        for button in buttons.all():
            if any(word in button.inner_text().lower() for word in ["accept", "agree", "ok"]):
                human_like_click(page, button)
                print("[🍪] Accepted cookies")
                break
    except Exception as e:
        print(f"[❌] Error accepting cookies: {e}")

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
                    print("[🔗] Clicked a safe link")
                    time.sleep(random.uniform(3, 7))
                    scroll_page(page)
    except Exception as e:
        print(f"[❌] Error during safe clicks: {e}")

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
    while True:
        if not proxies:
            print("[⚠️] No working proxies left! Refreshing...")
            proxies.extend(refresh_proxies())

        proxy = proxies.pop(0)
        device = get_random_device()
        print(f"[🌍] Using proxy: {proxy} with {device['browser']} for {url}")

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False, proxy={"server": proxy})
                context = browser.new_context(user_agent=device["user_agent"])
                page = context.new_page()

                enable_stealth(page)
                print(f"[🔍] Visiting: {url}")
                page.goto(url, timeout=90000)

                accept_cookies(page)
                scroll_page(page)
                safe_clicks(page)

                time.sleep(random.uniform(90, 150))
                browser.close()

        except Exception as e:
            print(f"[❌] Error visiting {url}: {e}")
            remove_failed_proxy(proxy, proxies)
            time.sleep(5)

# Start browsing
if __name__ == "__main__":
    print("[🚀] Script is starting...")
    num_threads = int(input("Enter number of threads: "))
    urls = load_urls()
    proxies = refresh_proxies()

    threads = [threading.Thread(target=visit_url, args=(random.choice(urls), proxies)) for _ in range(num_threads)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
