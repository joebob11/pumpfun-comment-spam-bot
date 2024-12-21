import requests
import logging
from time import sleep
import random
from threading import Thread
import subprocess
from termcolor import colored


""" VARS """
COMMENT = []
MINTS = []
PRINT_ERROR = True
COMMENT_PER_TOKEN = 1
DISABLE_PROXIES = False

""" LOGGING """
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)

""" SRC """
def post_comment(tokens, proxies, comment, mint):
    global DISABLE_PROXIES
    if DISABLE_PROXIES == False:
        current_proxy = random.choice(proxies)
        proxies = {
            'http': f'http://{current_proxy}',
            'https': f'http://{current_proxy}',
        }
    
    url = "https://client-proxy-server.pump.fun/comment"
    
    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.8",
        "content-type": "application/json",
        "origin": "https://pump.fun",
        "priority": "u=1, i",
        "referer": "https://pump.fun/",
        "sec-ch-ua": '"Brave";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "sec-gpc": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)",
        "x-aws-proxy-token": random.choice(tokens)
    }

    data = {
        "text": comment,
        "mint": mint
    }
    
    x = 0
    while x <= 5:
        x+=1
        try:
            if DISABLE_PROXIES == False:
                response = requests.post(url, json=data, headers=headers, proxies=proxies)
            else:
                response = requests.post(url, json=data, headers=headers)
            response_status_code = response.status_code
            if response_status_code == 200:
                logging.info(colored("Successfully commented on mint " + mint, "green"))
                break
            else:
                return
        except Exception as e:
            if PRINT_ERROR == True:
                logging.error(colored(f"Error commenting on mint {mint} - Unknown error: {e}", "red"))
                   

def find_new_mint(proxies):
    global DISABLE_PROXIES
    mint = ""
    if DISABLE_PROXIES == False:
        current_proxy = random.choice(proxies)
        proxies = {
            'http': f'http://{current_proxy}',
            'https': f'http://{current_proxy}',
        }
    try:
        if DISABLE_PROXIES == False:
            resp = requests.get("https://frontend-api.pump.fun/coins/latest", proxies=proxies)
        else:
            resp = requests.get("https://frontend-api.pump.fun/coins/latest")
        if resp.status_code == 200:
            mint = resp.json()["mint"]
    except Exception as ex:
        print(ex)
        pass
    return mint


def start_chromedriver():
    process = subprocess.Popen(["chromedriver.exe"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NO_WINDOW,
        start_new_session=True
    )
    return process
            
def load_sessions():
    tokens = []
    with open("tokens.txt", "r") as f:
        lines = f.read().split("\n")
        for line in lines:
            if line not in tokens and len(line) > 2:
                tokens.append(line.replace(" ", "").replace("\n", "").replace("\r", "").strip())
    return tokens

def load_proxies():
    proxies = []
    with open("proxies.txt", "r") as f:
        lines = f.read().split("\n")
        for line in lines:
            if line not in proxies and len(line) > 2:
                proxies.append(line.replace(" ", "").replace("\n", "").replace("\r", "").strip())
    return proxies

def load_comments():
    comments = []
    with open("comments.txt", "r") as f:
        lines = f.read().split("\n")
        for line in lines:
            if line not in comments and len(line) > 2:
                comments.append(line)
    return comments 
     
                
def main():
    global DISABLE_PROXIES
    Thread(target=(start_chromedriver)).start()
    tokens = load_sessions()
    proxies = load_proxies()
    comments = load_comments()
    if len(proxies) == 0:
        DISABLE_PROXIES = True
    logging.info(colored("Loaded: " + str(len(tokens)) + " tokens - " + str(len(proxies)) + " proxies - " + str(len(comments)) + " comments", "blue"))
    while True:
        mint = find_new_mint(proxies)
        if mint != "":
            if not mint in MINTS:
                MINTS.append(mint)
                for comment in comments:
                    x = 0
                    while x < COMMENT_PER_TOKEN:
                        Thread(target=(post_comment), args=(tokens, proxies, comment, mint)).start()
                        x+=1
        sleep(0.2)
        
if __name__ == "__main__":
    main()