import os
import sys
import requests
import time
import json
import random
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
from colorama import Fore, Style

RED = Fore.LIGHTRED_EX
YELLOW = Fore.LIGHTYELLOW_EX
GREEN = Fore.LIGHTGREEN_EX
BLUE = Fore.LIGHTBLUE_EX
WHITE = Fore.LIGHTWHITE_EX
BLACK = Fore.LIGHTBLACK_EX
MAGENTA = Fore.MAGENTA
RESET = Style.RESET_ALL

class TomarketBot:
    def __init__(self, datas, proxies):
        self.headers = {
            "host": "api-web.tomarket.ai",
            "connection": "keep-alive",
            "accept": "application/json, text/plain, */*",
            "user-agent": "Mozilla/5.0 (Linux; Android 10; REDmi 4A / 5A Build/QQ3A.200805.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/86.0.4240.185 Mobile Safari/537.36",
            "content-type": "application/json",
            "origin": "https://mini-app.tomarket.ai",
            "x-requested-with": "tw.nekomimi.nekogram",
            "sec-fetch-site": "same-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://mini-app.tomarket.ai/",
            "accept-language": "en-US,en;q=0.9",
        }

        # Default config
        self.datas              = datas
        self.proxies            = proxies
        self.use_proxy          = True if len(proxies) > 0 else False
        self.interval           = 1
        self.play_game          = True
        self.game_low_point     = 100
        self.game_high_point    = 150
        self.add_time_min       = 60
        self.add_time_max       = 120

    def create_requests_session(self, proxy=None):
        self.ses = requests.Session()
        if proxy is not None:
            self.ses.proxies.update({"http": proxy, "https": proxy})

    def set_authorization(self, auth):
        self.headers["authorization"] = auth

    def del_authorization(self):
        if "authorization" in self.headers.keys():
            self.headers.pop("authorization")

    def login(self, query_id):
        url = "https://api-web.tomarket.ai/tomarket-game/v1/user/login"
        data = json.dumps(
            {
                "init_data": query_id,
                "invite_code": "",
            }
        )
        self.del_authorization()

        res = self.http(url, self.headers, data)

        if res.status_code != 200:
            self.log(f"{RED}failed fetch token authorization, check http.log !")
            return None
        
        res_data = res.json().get("data")
        token = res_data.get("access_token")

        if token is None:
            self.log(f"{RED}failed fetch token authorization, check http.log !")
            return None
        
        return token
    
    def start_farming(self):
        data = json.dumps({"game_id": "53b22103-c7ff-413d-bc63-20f6fb806a07"})
        url = "https://api-web.tomarket.ai/tomarket-game/v1/farm/start"
        res = self.http(url, self.headers, data)
        if res.status_code != 200:
            self.log(f"{RED}failed start farming, check http.log last line !")
            return False

        data = res.json().get("data")
        end_farming = data["end_at"]
        format_end_farming = (
            datetime.fromtimestamp(end_farming).isoformat(" ").split(".")[0]
        )
        self.log(f"{GREEN}success start farming !")

    def end_farming(self):
        data = json.dumps({"game_id": "53b22103-c7ff-413d-bc63-20f6fb806a07"})
        url = "https://api-web.tomarket.ai/tomarket-game/v1/farm/claim"
        res = self.http(url, self.headers, data)
        if res.status_code != 200:
            self.log(f"{RED}failed start farming, check http.log last line !")
            return False

        poin = res.json()["data"]["claim_this_time"]
        self.log(f"{GREEN}success claim farming !")
        self.log(f"{GREEN}reward : {WHITE}{poin}")

    def daily_claim(self):
        url = "https://api-web.tomarket.ai/tomarket-game/v1/daily/claim"
        data = json.dumps({"game_id": "fa873d13-d831-4d6f-8aee-9cff7a1d0db1"})
        res = self.http(url, self.headers, data)
        if res.status_code != 200:
            self.log(f"{RED}failed claim daily sign,check http.log last line !")
            return False

        data = res.json().get("data")
        if isinstance(data, str):
            self.log(f"{YELLOW}maybe already sign in")
            return

        poin = data.get("today_points")
        self.log(
            f"{GREEN}success claim {BLUE}daily sign {GREEN}reward : {WHITE}{poin} !"
        )
        return

    def play_game_func(self, amount_pass):
        data_game = json.dumps({"game_id": "59bcd12e-04e2-404c-a172-311a0084587d"})
        start_url = "https://api-web.tomarket.ai/tomarket-game/v1/game/play"
        claim_url = "https://api-web.tomarket.ai/tomarket-game/v1/game/claim"
        for i in range(amount_pass):
            res = self.http(start_url, self.headers, data_game)
            if res.status_code != 200:
                self.log(f"{RED}failed start game !")
                return

            self.log(f"{GREEN}success {BLUE}start{GREEN} game !")
            self.countdown(30)
            point = random.randint(self.game_low_point, self.game_high_point)
            data_claim = json.dumps(
                {"game_id": "59bcd12e-04e2-404c-a172-311a0084587d", "points": point}
            )
            res = self.http(claim_url, self.headers, data_claim)
            if res.status_code != 200:
                self.log(f"{RED}failed claim game point !")
                continue

            self.log(f"{GREEN}success {BLUE}claim{GREEN} game point : {WHITE}{point}")
    
    def get_balance(self):
        url = "https://api-web.tomarket.ai/tomarket-game/v1/user/balance"
        while True:
            res = self.http(url, self.headers, "")
            if res.status_code != 200:
                self.log(f"{RED}failed fetch balance !")
                continue
            data = res.json().get("data")
            if data is None:
                self.log(f"{RED}failed get data !")
                return None

            timestamp = data["timestamp"]
            balance = data["available_balance"]
            self.log(f"{GREEN}balance : {WHITE}{balance}")
            if "daily" not in data.keys():
                self.daily_claim()
                continue

            if data["daily"] is None:
                self.daily_claim()
                continue

            next_daily = data["daily"]["next_check_ts"]
            if timestamp > next_daily:
                self.daily_claim()

            if "farming" not in data.keys():
                self.log(f"{YELLOW}farming not started !")
                result = self.start_farming()
                continue

            end_farming = data["farming"]["end_at"]
            format_end_farming = (
                datetime.fromtimestamp(end_farming).isoformat(" ").split(".")[0]
            )
            if timestamp > end_farming:
                self.end_farming()
                continue

            self.log(f"{YELLOW}not time to claim !")
            self.log(f"{YELLOW}end farming at : {WHITE}{format_end_farming}")
            if self.play_game:
                self.log(f"{GREEN}auto play game is enable !")
                play_pass = data.get("play_passes")
                self.log(f"{GREEN}game ticket : {WHITE}{play_pass}")
                if int(play_pass) > 0:
                    self.play_game_func(play_pass)
                    continue

            _next = end_farming - timestamp
            return _next + random.randint(self.add_time_min, self.add_time_max)
        
    def http(self, url, headers, data=None):
        while True:
            try:
                now = datetime.now().isoformat(" ").split(".")[0]
                if data is None:
                    res = self.ses.get(url, headers=headers, timeout=100)
                elif data == "":
                    res = self.ses.post(url, headers=headers, timeout=100)
                else:
                    res = self.ses.post(url, headers=headers, data=data, timeout=100)
                open("http.log", "a", encoding="utf-8").write(
                    f"{now} - {res.status_code} - {res.text}\n"
                )
                return res
            except requests.exceptions.ProxyError:
                print(f"{RED}bad proxy !")
                time.sleep(1)

            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                print(f"{RED}connection error / connection timeout !")
                time.sleep(1)
                continue

    def log(self, msg):
        now = datetime.now().isoformat(" ").split(".")[0]
        print(f"{BLACK}[{now}]{RESET} {msg}{RESET}")

    def countdown(self, t):
        for i in range(t, 0, -1):
            menit, detik = divmod(i, 60)
            jam, menit = divmod(menit, 60)
            jam = str(jam).zfill(2)
            menit = str(menit).zfill(2)
            detik = str(detik).zfill(2)
            print(f"{WHITE}waiting {jam}:{menit}:{detik}     ", flush=True, end="\r")
            time.sleep(1)
        print("                                        ", flush=True, end="\r")

    def work(self):
        list_countdown = []
        _start = int(time.time())

        no = 0
        for data in self.datas:
            proxy = None
            if self.use_proxy:
                proxy = self.proxies[no % len(self.proxies)]

            # Create session
            self.create_requests_session(proxy)

            # Infor to user the processing account
            self.log(
                f"{GREEN}Account number : {WHITE}{no+1}{GREEN}/{WHITE}{len(datas)} {GREEN}| Proxy : {WHITE}{proxy}"
            )

            # Get access token
            token = self.login(data)
            self.set_authorization(token)

            # Get balance
            result = self.get_balance()
            print_line()

            self.countdown(self.interval)
            list_countdown.append(result)
            no += 1

        _end = int(time.time())
        _tot = _end - _start
        
        # Filter None before find min
        list_countdown = [x for x in list_countdown if x is not None]

        _min = min(list_countdown) - _tot
        self.countdown(_min)

def clear_console():
    # For Windows
    if os.name == "nt":
        _ = os.system("cls")
    # For macOS and Linux
    else:
        _ = os.system("clear")

def print_banner():
    banner = f"""{ MAGENTA }
        
    ┏━┓┏━┓╋╋╋╋╋╋╋╋╋╋╋┏┓
    ┃┃┗┛┃┃╋╋╋╋╋╋╋╋╋╋╋┃┃
    ┃┏┓┏┓┣━━┳┓┏┳━━┳━┳┫┃┏┳━━┳━━┓
    ┃┃┃┃┃┃┏┓┃┗┛┃┃━┫┏╋┫┗┛┫┏┓┃━━┫
    ┃┃┃┃┃┃┏┓┣┓┏┫┃━┫┃┃┃┏┓┫┗┛┣━━┃
    ┗┛┗┛┗┻┛┗┛┗┛┗━━┻┛┗┻┛┗┻━━┻━━┛
                                                                        
        Auto Claim Bot For BinanceMoonBix
        Author  : Maverikos
        Github  : https://github.com/Maverikos
            { RESET }"""

    print(banner)

def print_line():
    print(WHITE + "~" * 60)

def browse_file(title, file_types):
    root = tk.Tk()
    root.withdraw()

    # Mở hộp thoại chọn file
    file_path = filedialog.askopenfilename(
        title=title,
        filetypes=file_types
    )

    return file_path

def load_data_from_file(file):
    return [i for i in open(file).read().splitlines() if len(i) > 0]

def format_proxy(proxy):
    # from ip:port:user:pass to http://user:pass@ip:port
    # if http format, just keep it
    if proxy.startswith('http'):
        return proxy
    parts = proxy.split(':')
    if len(parts) == 4:
        return f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
    else:
        return f"http://{parts[0]}:{parts[1]}"

# Define file types
DATA_FILE_TYPE = [("Text files", "*.txt"), ("All files", "*.*")]
PROXY_FILE_TYPE = [("Text files", "*.txt"), ("All files", "*.*")]

if __name__ == "__main__":
    try:
        # Show banner
        clear_console()
        print_banner()
        print_line()

        # Get datas
        data_file = browse_file("Select a Data File", [DATA_FILE_TYPE])
        if data_file:
            datas = load_data_from_file(data_file)
        else:
            datas = []

        # Get proxies
        proxy_file = browse_file("Select a Proxy File", [PROXY_FILE_TYPE])
        if proxy_file:
            proxies = load_data_from_file(proxy_file)
        else:
            proxies = []

        # Format proxies
        formatted_proxies = []
        for proxy in proxies:
            formatted_proxies.append(format_proxy(proxy))

        print(f"{GREEN}Total accounts        : {len(datas)}{RESET}")
        print(f"{GREEN}Total proxies detected: {len(proxies)}{RESET}")
        print_line()

        # Initialise the bot
        app = TomarketBot(datas, formatted_proxies)

        while(True):
            app.work()

    except KeyboardInterrupt:
        sys.exit()