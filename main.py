import requests
import warnings
import time
import hashlib
import qrcode
import os

warnings.filterwarnings("ignore")

project_id = "73710"
ticket_id = 0
screen_id = 0

day = "7月22日"
kind = "普通票"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Referer": f"https://show.bilibili.com/platform/detail.html?id={project_id}",
    "Accept": "*/*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7",
    "Cookie": "Cookies",
}

def md5value(key):
    input_name = hashlib.md5()
    input_name.update(key.encode("utf-8"))
    return input_name.hexdigest().lower()

def buy():
    global screen_id
    global ticket_id
    global price
    notify_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    try:
        check_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Referer": f"https://show.bilibili.com/platform/detail.html?id={project_id}",
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7",
        }
        url = f"https://show.bilibili.com/api/ticket/project/get?version=134&id={project_id}&project_id={project_id}"
        rsq = requests.get(url, headers=check_headers)
        data = rsq.json()['data']
        screen_list = data['screen_list']
        iday = 0
        ikind = 0
        ticket_list = []
        ticket_screen = ""
        ticket = ""
        while iday < len(screen_list):
            ticket_day_name = screen_list[iday]['name']
            if ticket_day_name == day:
                ticket_screen = screen_list[iday]
                ticket_list = ticket_screen['ticket_list']
                while ikind < len(ticket_list):
                    ticket_kind_name = ticket_list[ikind]['desc']
                    if ticket_kind_name == kind:
                        ticket = ticket_list[ikind]
                        ticket_id = ticket['id']
                        break
                    else:
                        ikind = ikind + 1
            iday = iday + 1
        screen_id = ticket_screen['id']
        clickable = ticket['clickable']
        price = ticket['price']
        if clickable == True:
            ticket_id = ticket['id']
            buyers = get_buyer()
            i = 0
            while i < len(buyers):
                token = prepare()
                buyer_info_list = []
                buyer_info = buyers[i]
                buyer_info_list.append(buyer_info)
                if token != "Error":
                    create_token = create(token, str(buyer_info_list).replace("'", '"'))
                    if create_token != "Error":
                        status(create_token)
                i = i + 1
        else:
            print(f"{notify_time}没货")
    except Exception as e:
        print("Error1")

def prepare():
    try:
        url = f"https://show.bilibili.com/api/ticket/order/prepare?project_id={project_id}"
        payload = {
                "project_id": int(project_id),
                "screen_id": int(screen_id),
                "order_type": 1,
                "count": 1,
                "sku_id": int(ticket_id),
                "token": "",
            }
        rsq = requests.post(url, headers=headers, json=payload)
        token = rsq.json()['data']['token']
        return token
    except Exception as e:
        return "Error2"

def get_buyer():
    url = f"https://show.bilibili.com/api/ticket/buyer/list?is_default&projectId={project_id}"
    rsq = requests.get(url, headers=headers)
    if rsq.json()['errno'] == 0:
        return rsq.json()['data']['list']

def create(token, buyer_info):
    try:
        url = f"https://show.bilibili.com/api/ticket/order/createV2?project_id={project_id}"
        payload = {
            "project_id": int(project_id),
            "screen_id": int(screen_id),
            "order_type": 1,
            "count": 1,
            "sku_id": int(ticket_id),
            "pay_money": price,
            "timestamp": int(round(time.time() * 1000)),
            "buyer_info": buyer_info,
            "token": token,
            "deviceId": md5value(str(round(time.time() * 1000))),
            }
        rsq = requests.post(url, headers=headers, json=payload)
        if rsq.json()['errno'] == 0:
            return rsq.json()['data']['token']
        else:
            return "Error"
    except Exception as e:
        return "Error3"

def status(token):
    try:
        url = f"https://show.bilibili.com/api/ticket/order/createstatus?token={token}&timestamp={str(int(round(time.time() * 1000)))}&project_id={project_id}"
        rsq = requests.get(url, headers=headers)
        if rsq.json()['errno'] == 0:
            payurl = rsq.json()['data']['payParam']['code_url']
            img = qrcode.make(payurl)
            img.save("qr.jpg")
            os.system("qr.jpg")
            print(payurl)
    except Exception as e:
        pass

def check_cookie():
    url = f"https://show.bilibili.com/api/ticket/buyer/list?is_default&projectId={project_id}"
    rsq = requests.get(url, headers=headers)
    if rsq.json()['errno'] == 2:
        tg_notify(1)
        mail_notify(1)
        return False
    else:
        return True

if __name__ == "__main__":
    i = 0
    while True:
        if i == 600:
            print("检测Cookie是否有效")
            if check_cookie() == False:
                print("Cookie过期")
                exit(0)
            i = 0
        buy()
        i = i + 1
        time.sleep(0.5)
