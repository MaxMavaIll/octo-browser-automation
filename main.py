import logging
import random
import toml
import asyncio

from octo_browser_integration.octo_pyppeteer import OctoBrowserPyppeteer
from projects.TestProject.test import test

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
log = logging.getLogger('octo')
config_toml = toml.load('config.toml')

async def process_profile(octo: OctoBrowserPyppeteer, profile):
    profile_id = profile['uuid']
    port = await octo.get_debug_port(profile_id)
    if port is None:
        return

    browser = await octo.get_browser(port)
    if browser is None:
        return

    page1 = await octo.open_new_tab(browser, profile_id)
    # page2 = await octo.open_new_tab(browser, profile_id)

    await test(octo, page1)

    await octo.close_current_tabs(profile_id)
    # await octo.stop_octo_profile(profile_id)

    await browser.disconnect()

async def main():
    config_toml = toml.load('config.toml')
    octo = OctoBrowserPyppeteer(
        url_api=config_toml['octo_browser']['URL_API'],
        url_local_api=config_toml['octo_browser']['URL_LOCAL_API'],
        token=config_toml['octo_browser']['TOKEN']
    )

    profiles = octo.get_registerable_profiles()

    semaphore = asyncio.Semaphore(4)

    async def sem_process(profile):
        async with semaphore:
            await process_profile(octo, profile)

    tasks = [asyncio.create_task(sem_process(profile)) for profile in profiles]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main())

