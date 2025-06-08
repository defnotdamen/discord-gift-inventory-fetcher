import requests
from time import strftime
import threading


promotion_id = "1379198759644303561"
claim_url = f"https://discord.com/api/v9/outbound-promotions/{promotion_id}/claim"

lock = threading.Lock() 


def load_tokens():
    tokens = []
    with open("tokens.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            if ':' in line and line.count(':') >= 2:
                token = line.split(':')[-1]
            else:
                token = line
            tokens.append(token)
    return tokens


def get_headers(token):
    return {
        "Authorization": token,
        "Content-Length": "0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Origin": "https://discord.com",
        "Referer": "https://discord.com/channels/@me",
        "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwi"
                              "c3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS"
                              "81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2"
                              "IChLSFRNTCwgbGlrZSBHZWNrbykiLCJicm93c2VyX3ZlcnNpb24iOiIxMTQuMC4wLjAiLC"
                              "Jvc192ZXJzaW9uIjoiMTAiLCJyZWZlcnJlciI6Imh0dHBzOi8vZGlzY29yZC5jb20vIn0=",
    }

def save_code(code):
    with lock:
        with open("gift_codes.txt", "a", encoding="utf-8") as f:
            f.write(f"{code}\n")


def claim_without_proxy(token):
    try:
        response = requests.post(claim_url, headers=get_headers(token), timeout=10)
        now = strftime("%H:%M:%S")
        if response.status_code == 200:
            data = response.json()
            code = data.get("code", "UNKNOWN_CODE")
            print(f"\033[90m{now} » \033[92mSUCCESS \033[97m• Claimed ExitLag code ➔ token \033[92m[{token}]\033[97m ➔ code \033[92m[{code}]\033[0m")
            save_code(code)
        else:
            print(f"\033[90m{now} » \033[91mERROR \033[97m• Failed to claim (HTTP {response.status_code}) ➔ token \033[91m[{token}]\033[0m")
    except Exception as e:
        now = strftime("%H:%M:%S")
        print(f"\033[90m{now} » \033[91mERROR \033[97m• Exception {e} ➔ token \033[91m[{token}]\033[0m")

def main():
    tokens = load_tokens()
    
    print(f"Extracting codes from {len(tokens)} tokens (no proxy)...")
    for token in tokens:
        claim_without_proxy(token)

if __name__ == "__main__":
    main()
