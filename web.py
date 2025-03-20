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

# Read URLs from file
def load_urls(file_path="urls.txt"):
    with open(file_path, "r") as file:
        return [line.strip() for line in file if line.strip()]

# Get current IP via Tor
def get_current_ip():
    try:
        response = requests.get(
            "https://check.torproject.org/api/ip",
            proxies={"http": TOR_SOCKS_PROXY, "https": TOR_SOCKS_PROXY},
            timeout=10
        )
        return response.json().get("IP", "Unknown")
    except Exception as e:
        print(f"[!] Error getting IP: {e}")
        return "Unknown"

# Change Tor IP before each thread starts
def change_tor_ip():
    try:
        with Controller.from_port(port=TOR_CONTROL_PORT) as controller:
            controller.authenticate(password=TOR_CONTROL_PASSWORD)
            controller.signal(Signal.NEWNYM)
            time.sleep(10)  
            print(f"[+] Tor IP changed successfully!")
    except Exception as e:
        print(f"[!] Error changing IP: {e}")

# Scroll page with random behavior
def scroll_page(page):
    try:
        scroll_time = random.randint(40, 50)
        for _ in range(scroll_time):
            scroll_px = random.choice([100, 200, 300])  
            page.evaluate(f"window.scrollBy(0, {scroll_px})")
            time.sleep(random.uniform(0.3, 1.5))
        print("[+] Scrolling complete")
    except Exception as e:
        print(f"[!] Error while scrolling: {e}")

# Accept cookies
def accept_cookies(page):
    try:
        buttons = page.locator("button")
        for button in buttons.all():
            text = button.inner_text().lower()
            if "accept" in text or "agree" in text or "ok" in text:
                button.click()
                print("[+] Accepted cookies/privacy notice")
                break
    except Exception as e:
        print(f"[!] Error accepting cookies: {e}")

# Perform random clicks
def random_clicks(page):
    try:
        links = page.locator("a")
        all_links = links.all()
        if all_links:
            num_clicks = random.randint(1, 3)
            for _ in range(num_clicks):
                link = random.choice(all_links)
                if link.is_visible():
                    link.click()
                    print("[+] Clicked a random link")
                    time.sleep(random.uniform(3, 7))
                    scroll_page(page)
    except Exception as e:
        print(f"[!] Error during random clicks: {e}")

# Visit URL
def visit_url(url):
    print(f"Changing IP for thread visiting: {url}")
    change_tor_ip()

    new_ip = get_current_ip()
    print(f"New IP: {new_ip} for {url}")

    user_agents = [
        # Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36",
        
        # macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7; rv:120.0) Gecko/20100101 Firefox/120.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_0) AppleWebKit/537.36 (KHTML, like Gecko) Safari/604.1.30",
        
        # Linux
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
        
        # Android
        "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 11; Pixel 4a) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 12; Samsung SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/17.0 Chrome/120.0.0.0 Mobile Safari/537.36",
        
        # iOS
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_1 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/16.1 Mobile/15E148 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/537.36",
        "Mozilla/5.0 (iPad; CPU OS 16_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/537.36",
    ]
    user_agent = random.choice(user_agents)

    retry = 0
    max_retries = 3
    while retry < max_retries:
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

                print(f"Visiting: {url} (Attempt {retry+1}/{max_retries})")
                page.goto(url, timeout=90000)  

                accept_cookies(page)
                scroll_page(page)
                random_clicks(page)

                time.sleep(random.uniform(90, 150))

                browser.close()
                print(f"Finished visiting: {url}")
                return  

        except Exception as e:
            print(f"[!] Error visiting {url}: {e}")
            retry += 1
            time.sleep(5)

    print(f"[!] Failed to load {url} after {max_retries} retries.")

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
        time.sleep(random.uniform(5, 10))  

    for thread in threads:
        thread.join()

# Continuous execution
if __name__ == "__main__":
    num_threads = int(input("Enter number of threads: "))
    while True:
        start_browsing(num_threads)
