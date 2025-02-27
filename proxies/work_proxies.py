


def load_new_proxies(updated_txt_file: str) -> list:
    with open(updated_txt_file, "r") as f:
        new_proxies = [line.strip().split(":") for line in f.readlines()] 
    return new_proxies

def get_update_list_proxies(using_proxies, path_txt_file: str = 'proxies/replece_proxies.txt') -> list:
    new_proxies = load_new_proxies(path_txt_file)
    new_proxies_dict = {ip: {"port": port, "login": login, "password": passwd} for ip, port, login, passwd in new_proxies}

    updated_proxies = []
    used_new_proxies = set()

    for index, proxy in enumerate(using_proxies):
        ip = proxy["ip"]
        if ip not in new_proxies_dict:
            for new_ip, new_prm in new_proxies_dict.items():
                if new_ip not in used_new_proxies:
                    updated_proxies.append({ 
                        f'{index+7}': {
                            "ip": new_ip, 
                            "port": new_prm['port'], 
                            "login": new_prm['login'], 
                            "password": new_prm['password']
                            }
                        }
                    )
                    used_new_proxies.add(new_ip)
                    break
        else:
            used_new_proxies.add(ip)

    return updated_proxies