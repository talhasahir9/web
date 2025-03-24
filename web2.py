import os
import time
import random
import threading
import requests
from playwright.sync_api import sync_playwright
from stem.control import Controller
from stem import Signal

# Tor settings
TOR_SOCKS_PROXY = "socks5://127.0.0.1:9150"
TOR_CONTROL_PORT = 9051
TOR_CONTROL_PASSWORD = "Tor123"

# Load URLs from file
def load_urls(file_path="urls.txt"):
    try:
        with open(file_path, "r") as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"[!] Error: {file_path} not found.")
        return []

# Get current IP via Tor
def get_current_ip():
    try:
        response = requests.get(
            "https://check.torproject.org/api/ip",
            proxies={"http": TOR_SOCKS_PROXY, "https": TOR_SOCKS_PROXY},
            timeout=10
        )
        return response.json().get("IP", "Unknown")
    except requests.RequestException as e:
        print(f"[!] Error getting IP: {e}")
        return "Unknown"

# Change Tor IP
def change_tor_ip():
    try:
        with Controller.from_port(port=TOR_CONTROL_PORT) as controller:
            controller.authenticate(password=TOR_CONTROL_PASSWORD)
            controller.signal(Signal.NEWNYM)
            time.sleep(random.uniform(10, 15))
            print(f"[+] Tor IP changed successfully!")
    except Exception as e:
        print(f"[!] Error changing IP: {e}")

# Scroll page randomly
def scroll_page(page):
    try:
        for _ in range(random.randint(65, 95)):
            scroll_px = random.choice([100, 200, 300, 500])
            page.evaluate(f"window.scrollBy(0, {scroll_px})")
            time.sleep(random.uniform(1, 3))
        print("[+] Scrolling complete")
    except Exception as e:
        print(f"[!] Error while scrolling: {e}")

# Accept cookies if prompted
def accept_cookies(page):
    try:
        buttons = page.locator("button")
        for button in buttons.all():
            text = button.inner_text().lower()
            if "accept" in text or "agree" in text or "ok" in text:
                time.sleep(random.uniform(2, 5))
                button.click()
                print("[+] Accepted cookies/privacy notice")
                break
    except Exception as e:
        print(f"[!] Error accepting cookies: {e}")

# Click "Next Page" or an internal link
def next_page_click(page):
    try:
        all_links = page.locator("a").all()
        visible_links = [link for link in all_links if link.is_visible()]
        next_page_links = [link for link in visible_links if link.inner_text().lower() in ["next", "next page", "continue", "→"]]
        internal_links = [link for link in visible_links if link.get_attribute("href") and not link.get_attribute("href").startswith("http")]

        if next_page_links:
            link = random.choice(next_page_links)
            time.sleep(random.uniform(3, 7))
            link.click()
            print("[+] Clicked 'Next Page'")
        elif internal_links:
            link = random.choice(internal_links)
            time.sleep(random.uniform(3, 7))
            link.click()
            print("[+] Clicked an internal article link")
        else:
            print("[!] No 'Next Page' or internal links found, skipping click.")
    except Exception as e:
        print(f"[!] Error during clicking: {e}")

# Stealth mode (no ad-blocking)
def apply_stealth(page):
    page.evaluate(
        """
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
        Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 4 });
        Object.defineProperty(navigator, 'userAgent', { get: () => navigator.userAgent.replace('Headless', '') });
        """
    )

# User agents (20 total)
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_1 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/16.1 Mobile/15E148 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; SM-G991U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/110.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_4) AppleWebKit/537.36 (KHTML, like Gecko) Safari/536.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_5 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/15.5 Mobile/15E148 Safari/537.36"
]

# Visit URL with stealth
def visit_url(url):
    print(f"Changing IP for thread visiting: {url}")
    change_tor_ip()

    new_ip = get_current_ip()
    print(f"New IP: {new_ip} for {url}")

    user_agent = random.choice(user_agents)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, proxy={"server": TOR_SOCKS_PROXY})
            context = browser.new_context(ignore_https_errors=True, user_agent=user_agent)
            page = context.new_page()

            apply_stealth(page)

            print(f"Visiting: {url}")
            page.goto(url, timeout=90000)

            accept_cookies(page)
            scroll_page(page)
            next_page_click(page)

            wait_time = random.uniform(15, 30)
            print(f"[+] Waiting {wait_time:.2f} seconds before visiting the next URL...")
            time.sleep(wait_time)

    except Exception as e:
        print(f"[!] Error visiting {url}: {e}")

    finally:
        try:
            context.close()
            browser.close()
            print(f"[+] Browser closed for {url}")
        except Exception as close_error:
            print(f"[!] Error closing browser: {close_error}")

# Multi-threading
def start_browsing(num_threads):
    urls = load_urls()
    if not urls:
        print("[!] No URLs found in urls.txt")
        return

    threads = []
    for _ in range(num_threads):
        url = random.choice(urls)
        thread = threading.Thread(target=visit_url, args=(url,))
        threads.append(thread)
        thread.start()
        time.sleep(random.uniform(5, 15))

    for thread in threads:
        thread.join()

# Continuous execution
if __name__ == "__main__":
    num_threads = int(input("Enter number of threads: "))
    while True:
        start_browsing(num_threads)
