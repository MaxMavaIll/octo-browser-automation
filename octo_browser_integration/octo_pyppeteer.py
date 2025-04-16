import json
import logging
import os
import aiohttp
import re
import requests
import toml

from pyppeteer import launch, connect
from captcha.api_captcha import CaptchaAPI
from google_sheets_integration.google_sheets import GoogleSheets
from octo_browser_integration.pyppeteer import PyppeteerHelper
from logging.handlers import TimedRotatingFileHandler


class OctoBrowserPyppeteer:
    ####### Proxies ########
    def update_proxies(self, profile_id, ip, port, login, password):
        data = {
            "proxy": { 
                "type": "socks5",
                "host": ip,
                "port": port,
                "login": login,
                "password": password
            }
        }

        response = requests.patch(self.url_api + f'/profiles/{profile_id}',  headers=self.headers, json=data)
        if response.status_code == 200:
            print(f"Profile {profile_id} updated")
        else:
            print(f"Error fetching profiles: {response.text}")
    
    ####### PROFILES #######
    def _fetch_profiles(self, tag: str):
        params = {
            "page_len": 100,
            "page": 0,
            "fields": "title,description,proxy,start_pages,tags,status,last_active",
            "search_tags": tag
        }

        response = requests.get(self.url_api + '/profiles', params=params, headers=self.headers)
        if response.status_code == 200:
            return response.json().get("data", [])
        else:
            print(f"Error fetching profiles: {response.text}")

        return []

    def get_registerable_profiles(self, title: str | list = 'test'):
        if isinstance(title, str):
            all_profiles = self._fetch_profiles(title)
            sorted_profiles = sorted(all_profiles, key=lambda x: int(re.search(r'\d+', x['title']).group()))
            return sorted_profiles

        elif isinstance(title, list):
            all_profiles = []
            for tag in title:
                all_profiles.extend(self._fetch_profiles(tag))

            sorted_profiles = sorted(all_profiles, key=lambda x: int(re.search(r'\d+', x['title']).group()))
            return sorted_profiles

        return []


    ####### Work with Windows #######
    async def start_octo_profile(self, profile_id):
        url = f'{self.url_local_api}/profiles/start'
        payload = {'uuid': profile_id, 'headless': False, 'debug_port': True}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:

                if response.status == 200:
                    return await response.json()
                else:
                    return await response.text

    async def stop_octo_profile(self, profile_id):
        url = f'{self.url_local_api}/profiles/stop'
        payload = {'uuid': profile_id, 'headless': False, 'debug_port': True}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return await response.text()

    async def get_debug_port(self, profile_id, name):
        for p in self.active_profiles:
            if p.get('uuid') == profile_id and p.get('state') == 'STARTED':
                self.log.info(f"{profile_id} | {name}-> {p.get('debug_port')}")
                if p.get('debug_port'):
                    return p.get('debug_port')
                await self.stop_octo_profile(profile_id)
            
        data = await self.start_octo_profile(profile_id)
        if isinstance(data, dict):
            return data.get('debug_port')
        return None

    def get_active_profiles_local(self):
        response = requests.get(f"{self.url_local_api}/profiles/active")
        if response.status_code == 200:
            return response.json()
        return []

    async def get_browser(self, port):
        try:
            url = f'http://127.0.0.1:{port}/json/version'
            response = requests.get(url)
            response.raise_for_status()
            ws_endpoint = response.json()['webSocketDebuggerUrl']
            self.browser = await connect(browserWSEndpoint=ws_endpoint)
            return self.browser
        except Exception as e:
            print(f"Error connecting to browser: {e}")
            return None



    ####### Interaction with windows #######
    async def open_new_tab(self, browser, profile_id):
        page = await browser.newPage()
        await page.goto('http://google.com')
        if profile_id not in self.pages:
            self.pages[profile_id] = []

        self.pages[profile_id].append(page)
        return page

    async def close_current_tabs(self, profile_id):
        if profile_id in self.pages:
            for page in self.pages[profile_id]:
                await page.close()
            del self.pages[profile_id]

    def update_data(self, data: dict):
        file_path = os.path.join('data', 'data.json')
        with open(file_path, 'w') as file:
            json.dump(data, file)

    def data_setup(self):
        LOG_DIR = "data"
        LOG_FILE = os.path.join(LOG_DIR, "data.json")

        if not os.path.exists(LOG_DIR):
            os.mkdir(LOG_DIR)
        
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'w') as file:
                json.dump({}, file)

        with open(LOG_FILE, 'r') as file:
            result = json.load(file)
        
        return result
    
    def update_password(self, config_profiles):
        for profile in config_profiles.values():
            password = self.config['PASSWORD'].copy()
            if profile['password']:
                password.insert(0, profile['password'])
            profile['password'] = password

        return config_profiles
    
    def log_setup(self):
        LOG_DIR = "logs"
        LOG_FILE = os.path.join(LOG_DIR, "app.log")

        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)

        if not os.path.exists(LOG_FILE):
            os.makedirs(LOG_DIR)

        LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

        file_handler = TimedRotatingFileHandler(LOG_FILE, when="midnight", interval=1, backupCount=7, encoding="utf-8")
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        file_handler.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        console_handler.setLevel(logging.INFO)

        logger = logging.getLogger("octo")
        logger.setLevel(logging.DEBUG)  # Мінімальний рівень логування
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        return logger

    def __init__(self, url_api: str, url_local_api: str, token: str):
        self.config = toml.load('config.toml')
        self.data = self.data_setup()
        self.log = self.log_setup()
        self.monitoring_version = False
        self.url_api = url_api
        self.url_local_api = url_local_api
        self.token = token
        self.headers = {'X-Octo-Api-Token': token, 'Content-Type': 'application/json'}
        self.active_profiles = self.get_active_profiles_local()
        self.pages = {}
        self.gg_sheet = GoogleSheets(url_sheets=self.config['google_sheet']['api'])
        self.captcha = CaptchaAPI(api_key=self.config['2captcha']['api_key'])
        self.helper_pyppeteer = PyppeteerHelper(catpcha=self.captcha, logger=self.log)


        network_accouts = self.gg_sheet.get_network_accout()
        self.info_networks = network_accouts["info_project"]
        self.info_accounts = self.update_password(network_accouts["info_profile"])
        