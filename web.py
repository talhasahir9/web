import time
import random
import requests
import socks
import socket
import threading
from stem.control import Controller
from stem import Signal
from fake_useragent import UserAgent

# Tor settings
SOCKS_PORT = 9050
CONTROL_PORT = 9051
TOR_PASSWORD = "your_tor_password"  # Use the actual password you set

socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", SOCKS_PORT)
socket.socket = socks.socksocket

TIER_1_COUNTRIES = {"US", "CA", "GB", "DE", "FR", "AU", "NZ"}  # Add more if needed

ua = UserAgent()  # Generate random user agents

def change_tor_ip():
    """Request a new Tor identity by sending a signal to the Tor control port."""
    with Controller.from_port(port=CONTROL_PORT) as controller:
        controller.authenticate(password=TOR_PASSWORD)
        controller.signal(Signal.NEWNYM)

def get_ip_info():
    """Fetch current IP and country using an external service."""
    try:
        headers = {"User-Agent": ua.random}
        response = requests.get("https://ipinfo.io/json", headers=headers, timeout=10)
        data = response.json()
        ip = data.get("ip", "Unknown")
        country = data.get("country", "Unknown")
        return ip, country
    except Exception:
        return "Unknown", "Unknown"

def visit_website(url):
    """Visit a website while ensuring the IP belongs to a Tier 1 country."""
    for _ in range(5):  # Try changing IP up to 5 times
        ip, country = get_ip_info()
        if country in TIER_1_COUNTRIES:
            try:
                headers = {"User-Agent": ua.random}
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    print(f"[✔] Visited {url} from {country} (IP: {ip})")
                    return
                else:
                    print(f"[✘] Failed to visit {url}. Status Code: {response.status_code}")
            except Exception as e:
                print(f"[!] Error visiting {url}: {e}")
        else:
            print(f"[!] Skipping IP: {ip} (Country: {country}) - Not Tier 1")
        
        print("[*] Changing Tor IP...")
        change_tor_ip()
        time.sleep(random.randint(5, 10))  # Wait for Tor to apply the new IP

def worker(urls):
    """Thread worker function to visit websites."""
    for url in urls:
        visit_website(url)
        wait_time = random.uniform(60, 150)  # Wait 1 to 2.5 minutes
        print(f"[*] Waiting {wait_time:.2f} seconds before next visit...")
        time.sleep(wait_time)

def main():
    """Load URLs and start multiple threads."""
    with open("urls.txt", "r") as file:
        urls = [line.strip() for line in file if line.strip()]
    
    num_threads = min(5, len(urls))  # Limit to 5 threads or number of URLs
    chunk_size = len(urls) // num_threads
    threads = []

    for i in range(num_threads):
        start = i * chunk_size
        end = None if i == num_threads - 1 else (i + 1) * chunk_size
        thread = threading.Thread(target=worker, args=(urls[start:end],))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
