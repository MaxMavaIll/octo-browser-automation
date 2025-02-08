from octo_browser_integration.octo_pyppeteer import OctoBrowserPyppeteer
from pyppeteer.page import Page


async def test(octo: OctoBrowserPyppeteer, page_registration: Page):
    await octo.helper_pyppeteer.enter_text(page_registration, "#APjFqb", "my ip")
    await page_registration.keyboard.press('Enter')
    await octo.helper_pyppeteer.random_sleep(5)
    await octo.helper_pyppeteer.click_element(page_registration, "//h3[contains(text(), 'What Is My IP Address - See Your Public Address - IPv4 & IPv6')]", by='xpath')
    