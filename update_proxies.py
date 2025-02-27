import toml

from proxies.work_proxies import get_update_list_proxies
from octo_browser_integration.octo_pyppeteer import OctoBrowserPyppeteer


def main():
    config_toml = toml.load('config.toml')
    octo = OctoBrowserPyppeteer(
        url_api=config_toml['octo_browser']['URL_API'],
        url_local_api=config_toml['octo_browser']['URL_LOCAL_API'],
        token=config_toml['octo_browser']['TOKEN']
    )

    profiles = octo.get_registerable_profiles(['GRASS', 'Grass2'])
    using_proxies = octo.gg_sheet.get_proxies()
    update_list = get_update_list_proxies(using_proxies)
    updated_list = list()
    
    if not update_list:
        print("No new proxies to update")
        return
    
    profiles_dict = {profile['title'].split(' ')[-1]: profile for profile in profiles}
    for proxy in update_list:
        proxy_id, proxy_data = next(iter(proxy.items()))
        profile = profiles_dict.get(proxy_id)

        if profile:
            print(f"Updating Profile: {profile['title']} with Proxy {proxy_data}")
            octo.update_proxies(profile['uuid'], **proxy_data)
            updated_list.append(proxy)

    octo.gg_sheet.update_proxies(updated_list)
    


if __name__ == '__main__':
    main()