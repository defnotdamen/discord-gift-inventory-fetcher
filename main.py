import requests
import time
import random
from time import strftime
import threading
from concurrent.futures import ThreadPoolExecutor

promotion_id = "1379198759644303561"
claim_url = f"https://discord.com/api/v9/outbound-promotions/{promotion_id}/claim"
lock = threading.Lock()
REQUEST_DELAY = 0.5  # Adjust for safety

# Load tokens
def load_tokens(limit=None):
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
            if limit and len(tokens) >= limit:
                break
    return tokens

# Load proxies from proxies.txt
def load_proxies():
    proxies = []
    with open("proxies.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if '@' in line:  # USER:PASS@IP:PORT
                auth, host = line.split('@')
                user, pw = auth.split(':')
                proxy = f"http://{user}:{pw}@{host}"
            else:
                proxy = f"http://{line}"  # IP:PORT
            proxies.append({
                "http": proxy,
                "https": proxy
            })
    return proxies

# Headers
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

def get_error_message(response):
    try:
        if "application/json" in response.headers.get("Content-Type", ""):
            return response.json().get("message", "No message")
        elif response.text:
            return response.text
        else:
            return "Empty response"
    except Exception:
        return "Unable to parse response"

# Claim per token
def claim_with_proxy(token, proxies):
    now = strftime("%H:%M:%S")
    time.sleep(REQUEST_DELAY)
    proxy = random.choice(proxies) if proxies else None
    try:
        response = requests.post(claim_url, headers=get_headers(token), timeout=10, proxies=proxy)
        status = response.status_code

        if "temporarily banned" in response.text.lower():
            print(f"\033[1;90m{now} » \033[1;91mRATE LIMIT \033[1;97m• IP temporarily blocked ➔ proxy: {proxy['http'] if proxy else 'none'}\033[0m")
            return

        if status == 200:
            data = response.json()
            code = data.get("code", "UNKNOWN_CODE")
            print(f"\033[1;90m{now} » \033[1;92mSUCCESS \033[1;97m• Claimed ➔ token \033[1;92m[{token}]\033[1;97m ➔ code \033[1;92m[{code}]\033[0m")
            save_code(code)

        elif status == 400:
            message = get_error_message(response)
            print(f"\033[1;90m{now} » \033[1;93mNOTICE \033[1;97m• Valid token, but claim failed ➔ \033[1;93m[{token}]\033[1;97m ➔ \033[1;93m[{message}]\033[0m")

        elif status == 401:
            print(f"\033[1;90m{now} » \033[1;91mINVALID \033[1;97m• Unauthorized ➔ \033[1;91m[{token}]\033[1;97m ➔ Invalid token\033[0m")

        elif status == 403:
            message = get_error_message(response)
            if "premium" in message.lower():
                print(f"\033[1;90m{now} » \033[1;94mSKIPPED \033[1;97m• Premium required ➔ \033[1;94m[{token}]\033[1;97m ➔ \033[1;94m[{message}]\033[0m")
            else:
                print(f"\033[1;90m{now} » \033[1;91mFORBIDDEN \033[1;97m• Access denied ➔ \033[1;91m[{token}]\033[1;97m ➔ \033[1;91m[{message}]\033[0m")

        else:
            msg = get_error_message(response)
            print(f"\033[1;90m{now} » \033[1;91mERROR \033[1;97m• HTTP {status} ➔ \033[1;91m[{token}]\033[1;97m ➔ \033[1;91m[{msg}]\033[0m")

    except Exception as e:
        print(f"\033[1;90m{now} » \033[1;91mERROR \033[1;97m• Exception {e} ➔ \033[1;91m[{token}]\033[0m")

# Main runner
def main():
    try:
        token_count = int(input("» INPUT • How many tokens to load? ➔ ").strip())
        thread_count = int(input("» INPUT • How many threads to run? ➔ ").strip())
    except ValueError:
        print("Please enter valid numbers.")
        return

    tokens = load_tokens(limit=token_count)
    proxies = load_proxies()

    if not proxies:
        print("WARNING: No proxies found in proxies.txt — all traffic will use your IP.\n")

    print(f"\nLoaded {len(tokens)} tokens and {len(proxies)} proxies. Starting with {thread_count} threads...\n")

    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        for token in tokens:
            executor.submit(claim_with_proxy, token, proxies)

if __name__ == "__main__":
    main()
