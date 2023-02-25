import requests
import re
import execjs
import os
from configparser import ConfigParser

current_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_path)

cfg = ConfigParser()
cfg.read("config.ini", encoding='utf-8')
username = cfg.get("userinfo", "username")
password = cfg.get("userinfo", "password")
test_url = cfg.get("config", "test_url")

mac = "000000000000"  # 不需要更改


def login():
    wlan_user_ip = ""
    wlan_ac_ip = ""
    try:
        response = requests.get(test_url, allow_redirects=False)
        jump_url = response.headers.get("Location")

        if response.status_code == 302 and jump_url.split("/")[2] == "172.20.30.1":
            paras = jump_url.split('?')[1].split('&')
            wlan_user_ip = paras[0].split('=')[1]
            wlan_ac_ip = paras[2].split('=')[1]
            print("需要登录")
        else:
            print("已经在线或未在校园网环境下")
            return False
    except Exception as e:
        print("网络出错")
        return False

    service_url = f"http://172.20.30.2:8080/Self/sso_login?login_method=1&wlan_user_ip={wlan_user_ip}&wlan_user_ipv6=&wlan_user_mac={mac}&wlan_ac_ip={wlan_ac_ip}&wlan_ac_name=&mac_type=1&authex_enable=&type=1"

    login_url = f"https://sso.dlut.edu.cn/cas/login?service=" + service_url

    session = requests.Session()
    response = session.get(login_url)

    lt = re.findall(r'name="lt" value="(.*?)"', response.text)[0]
    execution = re.findall(r'name="execution" value="(.*?)"', response.text)[0]
    jsessionidcas = response.cookies.get("JSESSIONIDCAS")
    with open('des.js') as f:
        ctx = execjs.compile(f.read())
    rsa = ctx.call('strEnc', username+password+lt, '1', '2', '3')

    login_data = {
        "rsa": rsa,
        "ul": len(username),  # 用户名长度
        "pl": len(password),  # 密码长度
        "sl": 0,  # 固定值0
        "lt": lt,
        "execution": execution,
        "_eventId": "submit"
    }

    response = session.post(login_url, data=login_data,
                            allow_redirects=False)

    ticket_url = response.headers.get("Location")
    if ticket_url is None:
        print("用户名或密码可能错误")
        return False

    ticket = ticket_url.split('&')[-1]

    dash_url = service_url + "&" + ticket

    session.get(dash_url)

    return True


if __name__ == '__main__':

    login()
    try:
        if requests.get(test_url, allow_redirects=False).status_code == 200:
            print("网络已畅通")
        else:
            print("登录失败")
    except:
        pass
