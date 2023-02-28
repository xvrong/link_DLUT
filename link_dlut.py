import re
import os
from configparser import ConfigParser
from time import sleep
import logging
import platform

import execjs
import requests
from ping3 import ping

current_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(current_path)

cfg = ConfigParser()
cfg.read("config.ini", encoding='utf-8')
username = cfg.get("userinfo", "username")
password = cfg.get("userinfo", "password")
test_url = cfg.get("config", "test_url")
check_interval = int(cfg.get("config", "check_interval"))
mac = "000000000000"  # 不需要更改


def get_log_path():
    log_path = ""

    sysstr = platform.system()
    if sysstr == "Windows":
        log_path = cfg.get("log", "log_path_windows")
    elif sysstr == "Linux":
        log_path = cfg.get("log", "log_path_linux")

    log_path = str.strip(log_path)

    if log_path == "":
        log_path = current_path

    if not os.path.exists(log_path):
        os.makedirs(log_path)

    return log_path


log_level = cfg.get("log", "log_level")
if log_level == "INFO":
    log_level = logging.INFO
elif log_level == "error":
    log_level = logging.ERROR

log_path = os.path.join(get_log_path(), "link_dlut.log")
logging.basicConfig(level=log_level, filename=log_path,
                    filemode="a", format="%(asctime)s - %(levelname)s: %(message)s", encoding="utf-8")

with open('des.js') as f:
    ctx = execjs.compile(f.read())


def login():
    wlan_user_ip = ""
    wlan_ac_ip = ""
    try:

        response = requests.get("http://" + test_url, allow_redirects=False)
        jump_url = response.headers.get("Location")

        if response.status_code == 200:
            logging.info("网络畅通，已登录或处于其他网络环境下")
            return True

        # 判断是否跳转到正确网址
        if response.status_code != 302 or jump_url.split("/")[2] != "172.20.30.1":
            logging.error("请检查设备是否处于校园网环境下")
            return False

        paras = jump_url.split('?')[1].split('&')
        wlan_user_ip = paras[0].split('=')[1]
        wlan_ac_ip = paras[2].split('=')[1]
        logging.info("正在登陆...")

    except Exception as e:
        logging.error("网络出错，请检查设备是否处于校园网环境下")
        logging.error("错误信息：" + str(e))
        return False

    service_url = f"http://172.20.30.2:8080/Self/sso_login?login_method=1&wlan_user_ip={wlan_user_ip}&wlan_user_ipv6=&wlan_user_mac={mac}&wlan_ac_ip={wlan_ac_ip}&wlan_ac_name=&mac_type=1&authex_enable=&type=1"

    login_url = f"https://sso.dlut.edu.cn/cas/login?service=" + service_url

    session = requests.Session()
    response = session.get(login_url)

    lt = re.findall(r'name="lt" value="(.*?)"', response.text)[0]
    execution = re.findall(r'name="execution" value="(.*?)"', response.text)[0]
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
        logging.error("用户名或密码错误")
        return False

    ticket = ticket_url.split('&')[-1]

    dash_url = service_url + "&" + ticket

    session.get(dash_url)
    logging.info("登录完成")
    if (delay := ping(test_url, unit='ms')) is None or delay == False:
        logging.error("完成登录后仍然无法使用网络，请检查账号是否欠费")
    else:
        logging.info(f"网络通畅，延迟为{delay}ms")

    return True


if __name__ == '__main__':
    login()  # 启动脚本，尝试登录
    while True:
        if (delay := ping(test_url, unit='ms', timeout=1)) is None or delay == False:
            login()
        else:
            logging.info(f"网络通畅，延迟为{delay}ms")
        sleep(check_interval)
