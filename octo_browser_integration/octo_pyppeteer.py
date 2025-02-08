import aiohttp
import re
import requests
import toml

from pyppeteer import launch, connect
from captcha.api_captcha import CaptchaAPI
from google_sheets_integration.google_sheets import GoogleSheets
from octo_browser_integration.pyppeteer import PyppeteerHelper


class OctoBrowserPyppeteer:
    


    def get_registerable_profiles(self):
        tag = 'test'
        params = {
            "page_len": 100,
            "page": 0,
            "fields": "title,description,proxy,start_pages,tags,status,last_active",
            "search_tags": tag
        }

        response = requests.get(self.url_api + '/profiles', params=params, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            sorted_profiles = sorted(data["data"], key=lambda x: int(re.search(r'\d+', x['title']).group()))
            # result = self.gg_sheet.get_registerable_profiles_gg_sh(sorted_profiles)
            return sorted_profiles
        return []

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

    async def get_debug_port(self, profile_id):
        for p in self.active_profiles:
            if p.get('uuid') == profile_id and p.get('state') == 'STARTED':
                print(f"{profile_id} -> {p.get('debug_port')}")
                return p.get('debug_port')
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

    async def open_new_tab(self, browser, profile_id):
        page = await browser.newPage()
        await page.goto('http://google.com')
        if profile_id not in self.pages:
            self.pages[profile_id] = []

        self.pages[profile_id].append(page)
        return page

    async def close_current_tabs(self, profile_id):
        for page in self.pages[profile_id]:
            await page.close()
        del self.pages[profile_id]

    def __init__(self, url_api: str, url_local_api: str, token: str):
        self.config = toml.load('config.toml')
        self.url_api = url_api
        self.url_local_api = url_local_api
        self.token = token
        self.headers = {'X-Octo-Api-Token': token}
        self.active_profiles = self.get_active_profiles_local()
        self.pages = {} 
        self.gg_sheet = GoogleSheets(url_sheets=self.config['google_sheet']['api'])
        self.captcha = CaptchaAPI(api_key=self.config['2captcha']['api_key'])
        self.helper_pyppeteer = PyppeteerHelper(catpcha=self.captcha)
