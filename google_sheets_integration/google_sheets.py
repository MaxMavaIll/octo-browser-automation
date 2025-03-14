import requests
import json
import toml

# config_toml = toml.load('config.toml')

# URL = {
#     "api_sheets": config_toml['gg_sheets']['url_sheets'],
# }

class GoogleSheets:
    def __init__(self, url_sheets: str):
        self.API = url_sheets

    ########################################
    #  GET
    ########################################

    def get_proxies(self) -> list:
        params = {"action": "get_proxies"}
        response = requests.get(self.API, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error requests to Apps Script: status {response.status_code}\ntext error: {response.text}")

    def get_network_accout(self) -> dict:
        params = {"action": "get_network_account_config"}
        response = requests.get(self.API, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error requests to Apps Script: status {response.status_code}\ntext error: {response.text}")


    ########################################
    #  POST
    ########################################

    def get_registerable_profiles_gg_sh(self, data: dict):
        json_data = json.dumps(data)

        response = requests.post(self.API, data={'action': 'get_profile_for_registration', 'data': json_data})
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error requests to Apps Script: status {response.status_code}\ntext error: {response.text}")


    def update_monitoring_data(self, data: dict):
        json_data = json.dumps(data)
        response = requests.post(self.API, data={'action': 'update_monitoring', 'data': json_data})
        if response.status_code == 200:
            print("Updated monitoring data")
        else:
            print(f"Error requests to Apps Script: status {response.status_code}\ntext error: {response.text}")


    def update_status_profile(self, title: str, status: str):
        json_data = json.dumps({'title': title, 'status': status})
        response = requests.post(self.API, data={'action': 'update_status_profile', 'data': json_data})
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error requests to Apps Script: status {response.status_code}\ntext error: {response.text}")

    def update_proxies(self, data):
        json_data = json.dumps(data)
        response = requests.post(self.API, data={'action': 'update_proxies', 'data': json_data})
        if response.status_code == 200:
            print(response.json())
        else:
            print(f"Error requests to Apps Script: status {response.status_code}\ntext error: {response.text}")
