import asyncio
import time
from twocaptcha import TwoCaptcha

class CaptchaAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        


    async def RecaptchaV2(self, google_site_key, page_url):
        solver = TwoCaptcha(self.api_key)
        max_attempts = 3

        for attempt in range(max_attempts):
            try:
                # Attempt to solve the reCAPTCHA
                result = await asyncio.to_thread(
                solver.recaptcha,
                sitekey=google_site_key,
                url=page_url
            )
                print("Recaptcha solution:", result['code'])
                return result['code']
            except Exception as e:
                print(f"Attempt {attempt} failed. Error: {e}")
                if attempt < max_attempts:
                    print("Retrying in", 3, "seconds...")
                    time.sleep(3)
                else:
                    print("Maximum attempts reached. Unable to solve CAPTCHA.")
                    return None

    # def get_task_result(task_id):
    #     url = f'https://2captcha.com/res.php?key={config_toml_all['api_key']}&action=get&id={task_id}&json=1'
    #     while True:
    #         response = requests.get(url)
    #         if response.json()['status'] == 1:
    #             return response.json()['request']
    #         time.sleep(5)