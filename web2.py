import os
import time
import random
import threading
import requests
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from stem.control import Controller
from stem import Signal

# Tor settings
TOR_SOCKS_PROXY = "socks5://127.0.0.1:9150"
TOR_CONTROL_PORT = 9051
TOR_CONTROL_PASSWORD = "Tor123"

# Read URLs from file
def load_urls(file_path="urls.txt"):
    try:
        with open(file_path, "r") as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"[!] Error: File '{file_path}' not found.")
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

# Change Tor IP before each thread starts
def change_tor_ip():
    try:
        with Controller.from_port(port=TOR_CONTROL_PORT) as controller:
            controller.authenticate(password=TOR_CONTROL_PASSWORD)
            controller.signal(Signal.NEWNYM)
            time.sleep(random.uniform(10, 15))  # Randomized wait time
            print("[+] Tor IP changed successfully!")
    except Exception as e:
        print(f"[!] Error changing IP: {e}")

# Scrolling with error handling
def scroll_page(page):
    try:
        for _ in range(random.randint(60, 85)):  # Randomized range
            scroll_px = random.choice([100, 200, 300, 500])
            page.evaluate(f"window.scrollBy(0, {scroll_px})")
            time.sleep(random.uniform(1, 3))  # More natural scrolling time
        print("[+] Scrolling complete")
    except Exception as e:
        print(f"[!] Error while scrolling: {e}")

# Accept cookies with safe element interaction
def accept_cookies(page):
    try:
        buttons = page.locator("button")
        for button in buttons.all():
            try:
                text = button.inner_text().lower()
                if any(kw in text for kw in ["accept", "agree", "ok"]):
                    time.sleep(random.uniform(2, 5))  # Human-like delay before clicking
                    button.click()
                    print("[+] Accepted cookies/privacy notice")
                    break
            except Exception:
                continue  # Continue if a button can't be interacted with
    except Exception as e:
        print(f"[!] Error accepting cookies: {e}")

# Click "Next Page" or an internal article
def next_page_click(page):
    try:
        all_links = page.locator("a").all()
        visible_links = [link for link in all_links if link.is_visible()]

        next_page_links = [
            link for link in visible_links if link.inner_text().strip().lower() in ["next", "next page", "continue", "→"]
        ]
        internal_links = [
            link for link in visible_links if link.get_attribute("href") and not link.get_attribute("href").startswith("http")
        ]

        if next_page_links:
            link = random.choice(next_page_links)
        elif internal_links:
            link = random.choice(internal_links)
        else:
            print("[!] No suitable links found, skipping click.")
            return
        
        time.sleep(random.uniform(3, 7))
        link.click()
        print(f"[+] Clicked link: {link.inner_text().strip()}")
    except Exception as e:
        print(f"[!] Error during clicking: {e}")

# Manual stealth mode
def apply_stealth(page):
    try:
        page.evaluate(
            """
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 4 });
            Object.defineProperty(navigator, 'userAgent', { get: () => navigator.userAgent.replace('Headless', '') });
            """
        )
    except Exception as e:
        print(f"[!] Error applying stealth mode: {e}")

# Visit URL with error handling and retry mechanism
def visit_url(url, max_retries=3):
    print(f"Changing IP for thread visiting: {url}")
    change_tor_ip()

    new_ip = get_current_ip()
    print(f"New IP: {new_ip} for {url}")

    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_1 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/16.1 Mobile/15E148 Safari/537.36",
    ]
    user_agent = random.choice(user_agents)

    retries = 0
    while retries < max_retries:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=False, 
                    proxy={"server": TOR_SOCKS_PROXY}
                )
                context = browser.new_context(
                    ignore_https_errors=True, 
                    user_agent=user_agent
                )
                page = context.new_page()

                apply_stealth(page)

                print(f"Visiting: {url}")
                page.goto(url, timeout=90000)

                accept_cookies(page)
                scroll_page(page)
                next_page_click(page)

                wait_time = random.uniform(15, 30)
                print(f"[+] Waiting {wait_time:.2f} seconds before next visit...")
                time.sleep(wait_time)

                break  # Exit retry loop if successful

        except PlaywrightTimeoutError:
            print(f"[!] Timeout error visiting {url}, retrying ({retries+1}/{max_retries})...")
        except Exception as e:
            print(f"[!] Error visiting {url}: {e}")
        finally:
            try:
                context.close()
                browser.close()
            except Exception:
                pass  # Ignore errors if browser already closed

        retries += 1

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
    try:
        num_threads = int(input("Enter number of threads: "))
        while True:
            start_browsing(num_threads)
    except KeyboardInterrupt:
        print("\n[!] Script interrupted by user. Exiting gracefully...")
