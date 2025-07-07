print("\033[38;5;88m" + r"""
                    ▓█████▄  ▄▄▄       ███▄ ▄███▓▓█████  ███▄    █
                    ▒██▀ ██▌▒████▄    ▓██▒▀█▀ ██▒▓█   ▀  ██ ▀█   █
                    ░██   █▌▒██  ▀█▄  ▓██    ▓██░▒███   ▓██  ▀█ ██▒
                    ░▓█▄   ▌░██▄▄▄▄██ ▒██    ▒██ ▒▓█  ▄ ▓██▒  ▐▌██▒
                    ░▒████▓  ▓█   ▓██▒▒██▒   ░██▒░▒████▒▒██░   ▓██░
                     ▒▒▓  ▒  ▒▒   ▓▒█░░ ▒░   ░  ░░░ ▒░ ░░ ▒░   ▒ ▒ 
                     ░ ▒  ▒   ▒   ▒▒ ░░  ░      ░ ░ ░  ░░ ░░   ░ ▒░
                     ░ ░  ░   ░   ▒   ░      ░      ░      ░   ░ ░ 
                       ░          ░  ░       ░      ░  ░         ░ 
                     ░                                             
""")


import requests
import time
import random
from time import strftime
import threading
from concurrent.futures import ThreadPoolExecutor
import os

EXITLAG_PROMO_ID = "1379198759644303561"
XBOX_PROMO_ID = "1389337666452983848"

lock = threading.Lock()
REQUEST_DELAY = 0.5


saved_codes = {}

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

def load_proxies():
    proxies = []
    try:
        with open("proxies.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if '@' in line:
                    auth, host = line.split('@')
                    user, pw = auth.split(':')
                    proxy = f"http://{user}:{pw}@{host}"
                else:
                    proxy = f"http://{line}"
                proxies.append({
                    "http": proxy,
                    "https": proxy
                })
    except FileNotFoundError:
        pass
    return proxies

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

def load_saved_codes(file_name):
    codes = set()
    if os.path.exists(file_name):
        with open(file_name, "r", encoding="utf-8") as f:
            for line in f:
                codes.add(line.strip())
    return codes

def save_code(code, file_name):
    global saved_codes
    if file_name not in saved_codes:
        saved_codes[file_name] = load_saved_codes(file_name)

    if code in saved_codes[file_name]:
        now = strftime("%H:%M:%S")
        
        print(f"\033[1;90m{now} » \033[1;93mDUPLICATE \033[1;97m• Code already saved ➔ \033[1;93m[{code}]\033[0m")
        return

    with lock:
        with open(file_name, "a", encoding="utf-8") as f:
            f.write(f"{code}\n")
    saved_codes[file_name].add(code)

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
def fetch_existing_codes(token, proxies):
    now = strftime("%H:%M:%S")
    proxy = random.choice(proxies) if proxies else None
    url = "https://discord.com/api/v9/users/@me/outbound-promotions/codes?locale=en-US"
    try:
        response = requests.get(url, headers=get_headers(token), timeout=10, proxies=proxy)
        if response.status_code == 200:
            data = response.json()
            if not data:
                print(f"\033[1;90m{now} » \033[1;94mINFO \033[1;97m• No promotions found ➔ \033[1;94m[{token}]\033[0m")
                return
            for promo in data:
                promo_name = promo.get("promotion", {}).get("outbound_title", "UNKNOWN")
                code = promo.get("code", "UNKNOWN_CODE")
                print(f"\033[1;90m{now} » \033[1;96mFOUND \033[1;97m• {promo_name} ➔ \033[1;96m[{token}]\033[1;97m ➔ \033[1;96m[{code}]\033[0m")
                file_name = f"{promo_name.lower().replace(' ', '_')}_codes.txt"
                save_code(code, file_name)
        else:
            msg = get_error_message(response)
            print(f"\033[1;90m{now} » \033[1;91mERROR \033[1;97m• Fetch failed ➔ \033[1;91m[{token}] ➔ [{msg}]\033[0m")
    except Exception as e:
        print(f"\033[1;90m{now} » \033[1;91mERROR \033[1;97m• Exception while fetching ➔ \033[1;91m[{e}]\033[0m")

def claim_promotion(token, proxies, promo_id, promo_name, file_name):
    now = strftime("%H:%M:%S")
    proxy = random.choice(proxies) if proxies else None
    time.sleep(REQUEST_DELAY)
    try:
        url = f"https://discord.com/api/v9/outbound-promotions/{promo_id}/claim"
        response = requests.post(url, headers=get_headers(token), timeout=10, proxies=proxy)
        status = response.status_code

        if "temporarily banned" in response.text.lower():
            print(f"\033[1;90m{now} » \033[1;91mRATE LIMIT \033[1;97m• IP temporarily blocked ➔ proxy: {proxy['http'] if proxy else 'none'}\033[0m")
            return

        if status == 200:
            data = response.json()
            code = data.get("code", "UNKNOWN_CODE")
            print(f"\033[1;90m{now} » \033[1;92mSUCCESS \033[1;97m• {promo_name} claimed ➔ \033[1;92m[{token}]\033[1;97m ➔ \033[1;92m[{code}]\033[0m")
            save_code(code, file_name)

        elif status == 400:
            msg = get_error_message(response)
            print(f"\033[1;90m{now} » \033[1;93mNOTICE \033[1;97m• {promo_name} claim failed ➔ \033[1;93m[{token}]\033[1;97m ➔ \033[1;93m[{msg}]\033[0m")

        elif status == 401:
            print(f"\033[1;90m{now} » \033[1;91mINVALID \033[1;97m• Unauthorized ➔ \033[1;91m[{token}]\033[1;97m ➔ Invalid token\033[0m")

        elif status == 403:
            msg = get_error_message(response)
            if "premium" in msg.lower():
                print(f"\033[1;90m{now} » \033[1;94mSKIPPED \033[1;97m• {promo_name} ➔ Premium required ➔ \033[1;94m[{msg}]\033[0m")
            else:
                print(f"\033[1;90m{now} » \033[1;91mFORBIDDEN \033[1;97m• {promo_name} ➔ {msg} ➔ \033[1;91m[{token}]\033[0m")

        else:
            msg = get_error_message(response)
            print(f"\033[1;90m{now} » \033[1;91mERROR \033[1;97m• HTTP {status} ➔ {promo_name} ➔ \033[1;91m[{msg}]\033[0m")

    except Exception as e:
        print(f"\033[1;90m{now} » \033[1;91mERROR \033[1;97m• Exception in {promo_name} ➔ \033[1;91m[{e}]\033[0m")

def claim(token, proxies, mode):
    if mode == "xbox":
        claim_promotion(token, proxies, XBOX_PROMO_ID, "XBOX", "xbox_codes.txt")
    elif mode == "exitlag":
        claim_promotion(token, proxies, EXITLAG_PROMO_ID, "EXITLAG", "exitlag_codes.txt")
    elif mode == "both":
        claim_promotion(token, proxies, XBOX_PROMO_ID, "XBOX", "xbox_codes.txt")
        claim_promotion(token, proxies, EXITLAG_PROMO_ID, "EXITLAG", "exitlag_codes.txt")
    elif mode == "fetch":
        fetch_existing_codes(token, proxies)


def main():
    try:
        now = strftime("%H:%M:%S")
        thread_count = int(input(f"\033[1;96m[{now}] » INPUT • \033[1;97mHow many threads to run? ➔ \033[0m").strip())
        mode = input(f"\033[1;96m[{now}] » INPUT • \033[1;97mMode [xbox / exitlag / both / fetch] ➔ \033[0m").strip().lower()
        if mode not in {"xbox", "exitlag", "both", "fetch"}:
            print("\033[1;91mInvalid mode. Choose 'xbox', 'exitlag', 'both', or 'fetch'.\033[0m")
            return
    except ValueError:
        print("\033[1;91mPlease enter valid numbers.\033[0m")
        return



    tokens = load_tokens()
    proxies = load_proxies()

    if not proxies:
        print("\033[1;93mWARNING: No proxies found in proxies.txt — all traffic will use your IP.\033[0m\n")

    print(f"\nLoaded {len(tokens)} tokens and {len(proxies)} proxies. Starting with {thread_count} threads in '{mode}' mode...\n")

    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        for token in tokens:
            executor.submit(claim, token, proxies, mode)

if __name__ == "__main__":
    main()
