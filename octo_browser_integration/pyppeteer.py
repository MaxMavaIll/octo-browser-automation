import asyncio
import random
import sys
import time


from captcha.api_captcha import CaptchaAPI
from pyppeteer.page import Page

class PyppeteerHelper:

    async def random_sleep(self, min_sec: int = 2, max_sec: int = 4):
        if min_sec >= max_sec:
            await asyncio.sleep(min_sec)
            return
        
        sleep_time = random.uniform(min_sec, max_sec)
        print(f"Sleeping for {sleep_time} seconds")
        await asyncio.sleep(sleep_time)

    async def enter_text(self, page: Page, selector: str, text: str, by: str = "css"):
        if by.lower() == "css":
            await page.waitForSelector(selector)
            await page.type(selector, text)
        elif by.lower() == "xpath":
            elements = await page.xpath(selector)
            if elements:
                await elements[0].type(text)
        else:
            raise ValueError("Параметр 'by' повинен бути 'css' або 'xpath'")
        await self.random_sleep()

    async def click_element(self, page: Page, selector: str, by: str = "css"):
        if by.lower() == "css":
            await page.waitForSelector(selector)
            await page.click(selector)
        elif by.lower() == "xpath":
            elements = await page.xpath(selector)
            if elements:
                await elements[0].click()
        else:
            raise ValueError("Параметр 'by' повинен бути 'css' або 'xpath'")
        await self.random_sleep()

    async def clean_input(self, page: Page, selector: str, by: str = "css"):
        if by.lower() == "css":
            await page.waitForSelector(selector)
            await page.evaluate(f'document.querySelector("{selector}").value = "";')

        elif by.lower() == "xpath":
            element = await page.waitForXPath(selector)
            await page.evaluate('(el) => el.value = ""', element)
        else:
            raise ValueError("Параметр 'by' повинен бути 'css' або 'xpath'")
        await self.random_sleep()

    async def clean_input_key(self, page: Page, selector: str, by: str = "css"):
        if by.lower() == "css":
            await page.waitForSelector(selector)
            element = await page.querySelector(selector)
        elif by.lower() == "xpath":
            element = await page.waitForXPath(selector)
        else:
            raise ValueError("Параметр 'by' повинен бути 'css' або 'xpath'")

        
        await element.click()
        await page.evaluate('document.execCommand("selectAll")')
        # await page.keyboard.down(modifier_key)
        # await page.keyboard.press("A")
        # await page.keyboard.up(modifier_key)
        await page.keyboard.press('Backspace')
        await self.random_sleep()

    async def get_element_text(self, page: Page, selector: str, by: str = "css"):
        if by.lower() == "css":
            element = await page.querySelector(selector)
            if not element:
                return None
            text = await page.evaluate('(el) => el?.innerText', await page.querySelector(selector))
        elif by.lower() == "xpath":
            element = await page.xpath(selector)
            if not element:
                return None
            text = await page.evaluate('(el) => el?.innerText', element[0])

        return text

    async def switch_to_iframe(self, page: Page, selector: str):
        await page.waitForSelector(selector)
        element = await page.querySelector(selector)
        frame = await element.contentFrame()
        return frame

    async def solve_recaptcha(self, page: Page,  url_site):
        recaptcha_frame = await self.switch_to_iframe(page, "iframe[src*='recaptcha']")
        await recaptcha_frame.waitForSelector("#recaptcha-anchor")
        anchor = await recaptcha_frame.querySelector("#recaptcha-anchor")
        await anchor.click()
        await self.random_sleep()

        aria_checked = await recaptcha_frame.evaluate('(element) => element.getAttribute("aria-checked")', anchor)
        
        if aria_checked == "false":
            with open('captcha/findRecaptchaClients.js', 'r', encoding='utf-8') as file:
                script = file.read()
            results = await page.evaluate(script)
            
            sitekey = results[0]['sitekey']
            callback = results[0]['callback']
            print(f"Sitekey: {sitekey}")
            print(f"Callback: {callback}")
            
            captcha_solution = await self.captcha.RecaptchaV2(sitekey, url_site)
            if captcha_solution is None:
                return
            
            await page.evaluate(f"{callback}(\"{captcha_solution}\");")



    def __init__(self, catpcha: CaptchaAPI):
        self.captcha = catpcha