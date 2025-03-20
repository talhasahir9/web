# **📖 ReadMe: Advanced Organic Traffic Generator**  

This script **automates website visits** using **Tor** for anonymity, **random user agents** for fingerprint spoofing, and **human-like behavior** such as **scrolling, clicking, and waiting**.  

---

## **🔹 Features**
✔ **Multi-threaded browsing** – Multiple sites visited at once.  
✔ **Tor IP Rotation** – Each visit gets a new identity.  
✔ **Randomized User Agents** – Mimics real users from various devices.  
✔ **Scrolling & Clicks** – Looks like real human browsing.  
✔ **Cookie Consent Handling** – Accepts cookies automatically.  
✔ **Runs Continuously** – Loops indefinitely for automated visits.  

---

## **🔹 Installation Guide**  
### **1️⃣ Install Required Dependencies**
Make sure you have **Python 3.8+** installed. Then, install dependencies:  
```bash
pip install playwright requests stem
```
⚡ **Initialize Playwright Browsers:**  
```bash
playwright install
```

### **2️⃣ Install & Configure Tor**
#### **🔹 Linux (Ubuntu/Debian)**
```bash
sudo apt update && sudo apt install tor
```
#### **🔹 Windows**
1. Download Tor Browser from: [https://www.torproject.org/download/](https://www.torproject.org/download/)  
2. Enable **ControlPort 9051** in `torrc` configuration file.  

#### **🔹 Start Tor Service**
Run:  
```bash
tor &
```
Or on Windows, **open Tor Browser** before running the script.  

---

## **🔹 How to Use**  
1. **Add URLs to `urls.txt`** (one per line).  
2. **Run the script:**  
```bash
python script.py
```
3. **Enter number of threads** when prompted.  

---

## **🔹 How It Works**
1. **Fetches a URL from `urls.txt`**  
2. **Changes Tor IP** before visiting the site.  
3. **Uses a random User-Agent** for each visit.  
4. **Loads the website** in Playwright-controlled browser.  
5. **Accepts cookies** if a consent popup appears.  
6. **Scrolls for 40-50 seconds** before interacting.  
7. **Clicks random links**, then **scrolls for 5-10 sec** after clicks.  
8. **Waits 90-150 seconds** before closing the browser.  
9. **Repeats with a new IP**  

---

## **🔹 Customization Options**
- **Change scroll behavior** in `scroll_page()`
- **Modify time delays** in `time.sleep()`
- **Adjust random clicks** in `random_clicks()`

---

## **🔹 Notes & Limitations**
⚠ **Requires Tor running in the background.**  
⚠ **Websites with strong bot detection may still block visits.**  
⚠ **Performance depends on system and internet speed.**  

---

### **🚀 Now you're ready to generate organic traffic!** 🎯
