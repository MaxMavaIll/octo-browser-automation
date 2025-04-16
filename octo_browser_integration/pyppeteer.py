import asyncio
import random
import sys
import time
import logging


from captcha.api_captcha import CaptchaAPI
from pyppeteer.page import Page

class PyppeteerHelper:
    async def safe_wait_for_xpath(self, page: Page, selector, timeout=20000):
        try:
            element = await page.waitForXPath(selector, timeout=timeout)
            return element
        except Exception as e :
            self.log.error(f"Element not found by xpath:{selector}\nError: {e}")
            return None
        
    async def safe_wait_for_selector(self, page: Page, selector, timeout=20000):
        try:
            element = await page.waitForSelector(selector, timeout=timeout)
            return element
        except Exception as e :
            self.log.error(f"Element not found by css: {selector}\nError: {e}")
            return None

    async def random_sleep(self, min_sec: int = 2, max_sec: int = 4):
        if min_sec >= max_sec:
            await asyncio.sleep(min_sec)
            return
        
        sleep_time = random.uniform(min_sec, max_sec)
        self.log.info(f"Sleeping for {sleep_time} seconds")
        await asyncio.sleep(sleep_time)

    async def enter_text(self, page: Page, selector: str, text: str, by: str = "css"):
        if by.lower() == "css":
            elements = await self.safe_wait_for_selector(page, selector)
            if elements:
                await page.type(selector, text)
        elif by.lower() == "xpath":
            elements = await self.safe_wait_for_xpath(page, selector)
            if elements:
                await elements.type(text)
        else:
            raise ValueError("Параметр 'by' повинен бути 'css' або 'xpath'")
        await self.random_sleep()

    async def click_element(self, page: Page, selector: str, by: str = "css"):
        if by.lower() == "css":
            elements = await self.safe_wait_for_selector(page, selector)
            if elements:
                await elements.click(selector)
        elif by.lower() == "xpath":
            elements = await self.safe_wait_for_xpath(page, selector)
            if elements:
                await elements.click()
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
            element = await self.safe_wait_for_selector(page, selector)
        elif by.lower() == "xpath":
            element = await self.safe_wait_for_xpath(page, selector)
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
            element = await self.safe_wait_for_selector(page, selector)
            if not element:
                return None
            text = await page.evaluate('(el) => el?.innerText', element)
        elif by.lower() == "xpath":
            element = await self.safe_wait_for_xpath(page, selector)
            if not element:
                return None
            text = await page.evaluate('(el) => el?.innerText', element)

        return text

    async def test_js_injection(self, page: Page):
        iframe_selector = 'iframe[src*="challenges.cloudflare.com"]'

        iframe_handle = await page.evaluateHandle('''() => {
            const shadowHost = document.querySelector('#uATa8');
            if (!shadowHost) return null;
            
            let iframe = null;
            if (shadowHost.shadowRoot) {
                iframe = shadowHost.shadowRoot.querySelector('iframe[src*="challenges.cloudflare.com"]');
            }
            return iframe;
        }''')

        if iframe_handle:
            iframe = iframe_handle.asElement()
            iframe = await iframe.contentFrame()
        else:
            print("Iframe не знайдений")

    async def switch_to_iframe(self, page: Page, selector: str):
        element = await self.safe_wait_for_selector(page, selector)
        if not element:
            return None
        frame = await element.contentFrame()
        return frame
    
    async def solve_cloudflare(self, page: Page, selector_block_checker: str, selector_check_mark: str):
        anchor = await self.safe_wait_for_selector(page, selector_block_checker)
        if not anchor:
            return
        
        box = await anchor.boundingBox()
        x = box['x'] + box['width'] * 0.08  # приблизно 8% від лівого краю
        y = box['y'] + box['height'] * 0.5
        await page.mouse.click(x, y)

    async def solve_recaptcha(
            self, 
            page: Page,  
            url_site: str = None, 
            selector_block_checker: str = "iframe[src*='recaptcha']", 
            selector_check_mark: str = "#recaptcha-anchor",
            name_checker: str = None
            ):
        """
        EXAMPLE:
        selector_block_checker = "iframe[src*='recaptcha']"
        selector_check_mark = "#recaptcha-anchor"
        """
 
        
        recaptcha_frame = await self.switch_to_iframe(page, selector_block_checker)
        if not recaptcha_frame:
            return
        
        anchor = await self.safe_wait_for_selector(page, selector_check_mark)
        await anchor.click()
        await self.random_sleep()

        if name_checker == "Recaptcha3":

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



    def __init__(self, catpcha: CaptchaAPI, logger: logging.Logger):
        self.captcha = catpcha
        self.log = logger