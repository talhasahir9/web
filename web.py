import undetected_chromedriver as uc
import random
import time
import threading
import requests
from fake_useragent import UserAgent
from stem import Signal
from stem.control import Controller

# List of Tier 1 countries
TIER_1_COUNTRIES = {"US", "CA", "GB", "AU", "DE", "FR"}

# Load URLs from file
def load_urls():
    with open("urls.txt", "r") as file:
        return [line.strip() for line in file if line.strip()]

# Change Tor IP
def change_tor_ip():
    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password="your_tor_password")  # Set Tor control password
        controller.signal(Signal.NEWNYM)
        time.sleep(10)  # Allow time for IP change

# Get current Tor IP and country
def get_tor_ip_country():
    try:
        proxies = {"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"}
        ip_info = requests.get("https://ipinfo.io/json", proxies=proxies, timeout=10).json()
        return ip_info.get("ip", "Unknown"), ip_info.get("country", "Unknown")
    except:
        return "Unknown", "Unknown"

# Initialize
URLS = load_urls()
NUM_THREADS = 5  # Adjust as needed
ua = UserAgent()

def visit_website():
    """Visits a website only if the Tor IP is from a Tier 1 country."""
    while True:
        url = random.choice(URLS)

        # Keep changing Tor IP until we get a Tier 1 country
        while True:
            tor_ip, country = get_tor_ip_country()
            if country in TIER_1_COUNTRIES:
                break  # Use this IP
            print(f"Skipping IP: {tor_ip} (Country: {country}) - Not Tier 1")
            change_tor_ip()  # Change IP and try again

        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument("--proxy-server=socks5h://127.0.0.1:9050")  # Use Tor proxy
        chrome_options.add_argument(f"user-agent={ua.random}")  # Random User-Agent
        chrome_options.add_argument("--headless=new")  # Run headless
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid detection

        # Start undetected browser
        driver = uc.Chrome(options=chrome_options)
        
        try:
            driver.get(url)
            time.sleep(random.uniform(10, 30))  # Simulate human browsing
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # Scroll down
            time.sleep(random.uniform(5, 15))  # Stay longer on the page
            
            print(f"Visited: {url} | IP: {tor_ip} | Country: {country} ✅")
        
        except Exception as e:
            print(f"Error visiting {url}: {e}")
        finally:
            driver.quit()  # Close browser

        change_tor_ip()  # Change IP after each request
        time.sleep(random.uniform(30, 120))  # Wait before next visit

# Start multiple threads
threads = []
for _ in range(NUM_THREADS):
    thread = threading.Thread(target=visit_website)
    thread.start()
    threads.append(thread)

# Keep the threads running
for thread in threads:
    thread.join()