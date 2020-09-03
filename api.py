import requests
from tools import get_fake_headers, log, get_time
from config import *
from datetime import datetime, timedelta
import re
import time


def login(account, password)->requests.Session:
    url = "http://bdhq.ncepu.edu.cn/ncepucenter/weixinlogin.json"
    session = requests.Session()
    data = {
        'reg_name': account,
        'password': password,
    }
    res = session.post(url, data=data, headers=get_fake_headers())
    if res.json()['success']:
        log(f"login {account} successfully")
        return session
    log(f"login {account} failed {res.text}")
    exit(-1)

def logout(session:requests.Session):
    url = "http://bdhq.ncepu.edu.cn/ncepucenter/common_logout.t"
    res = session.get(url, headers=get_fake_headers())
    if res.status_code == 200:
        log("session logout successfully")
    else:
        log(f"session logout failed {res.text}")
        exit(-1)

def order_homepage(session:requests.Session, account):
    order_show_url = f"http://yushiyuyue.ncepu.edu.cn/openHomePage?openid={account}"
    _ = session.get(order_show_url, headers=get_fake_headers())
    order_show_url = "http://yushiyuyue.ncepu.edu.cn/openHomePage"
    return session.get(order_show_url, headers=get_fake_headers())

def available_order_list(session:requests.Session, account, appointdate):
    if re.match("^\d{4}-\d{2}-\d{2}$", appointdate) == None:
        log(f"order_list {appointdate} format wrong!")
        exit(-1)
    if datetime(year=int(appointdate[:4]), month=int(appointdate[5:7]), day=int(appointdate[8:]), hour=23, minute=59) \
        < datetime.now():
        log(f"wrong datetime {appointdate}")
        return []
    _ = order_homepage(session, account)
    url = "http://yushiyuyue.ncepu.edu.cn/appointRules/queryAppointRules"
    data = {
        'goodsid': 14,
        'appointdate': appointdate
    }
    res = session.post(url, data=data, headers=get_fake_headers())
    res = res.json()
    if res['returncode'] == 'SUCCESS':
        log('get order_list successfully')
        res = res['jsonArr']
        for one in res:
            start = one['timeslot'].split('-')
            end = start[1]
            start = start[0]
            one['start'] = timedelta(hours=float(start[:2]), minutes=float(start[3:]))
            one['end'] = timedelta(hours=float(end[:2]), minutes=float(end[3:]))
            if one['msg'] == '已约满':
                one['msg'] = 0
            else:
                one['msg'] = int(one['msg'])
        return res
    else:
        log('get order_list failed')
        exit(-1)

def ordered_bath_list(session:requests.Session):
    _ = order_homepage(session, config_account)
    url = "http://yushiyuyue.ncepu.edu.cn/openCustomerOrderList"
    res = session.get(url, headers=get_fake_headers())
    if res.status_code != 200:
        log(f"get ordered_bath_list failed {res.text}")
        logout(session)
        exit(-1)
    res = res.text
    ordered_number = re.findall("&quot;\d+&", res)
    ordered_number = [re.findall("\d+", x)[0] for x in ordered_number]
    ordered_time = re.findall("&quot;\d{4}-\d{2}-\d{2} \d{2}:\d{2}-\d{2}:\d{2}", res)
    ordered_time = [x[6:] for x in ordered_time]
    assert len(ordered_number) == len(ordered_time)
    return ordered_number, ordered_time

def order_bath(session:requests.Session, account, appointdate, rulesid):
    _ = available_order_list(session, account, config_appointdate)
    bathroomid = '14'
    sex = '1'
    goodslogo = "http://59.67.246.90:8088/photo/0001/f7f4b326beff45a6a848a8b1c9b53b68.png"
    bathroomname = '二校男浴室'
    data = {
        'bathroomid': bathroomid,
        'appointdate': appointdate,
        'rulesid': rulesid,
        'sex': sex,
        'goodslogo': goodslogo,
        'bathroomname': bathroomname,
    }
    order_url = "http://yushiyuyue.ncepu.edu.cn/appointmentGoods"
    res = session.post(order_url, data=data, headers=get_fake_headers())
    res = res.json()
    return res['returncode'] == 'SUCCESS'

def cancel_order(session:requests.Session, cancel_set=None):
    assert isinstance(cancel_set, set) or cancel_set == None
    url = "http://yushiyuyue.ncepu.edu.cn/cancelGoodsOrder"
    ordered_number, ordered_time = ordered_bath_list(session)
    if len(ordered_number) == 0:
        log("当前未查询到已预约记录，请检查")
        logout(session)
        exit(-1)
    if not cancel_set:
        tip = "请输入要取消预约的编号，确认请输入exit，取消已选择的请输入clear"
        cancel_set = set()
        while True:
            print(tip, f"当前已选{len(cancel_set)}个 为", cancel_set)
            print(f"已预约编号如下，共{len(ordered_number)}个")
            for i in range(len(ordered_number)):
                suffix = "已选择" if i in cancel_set else ""
                print(f"编号：{i}  预约时间：{ordered_time[i]}  {suffix}")
            temp = input()
            if temp == 'exit': break
            elif temp == 'clear':
                cancel_set.clear()
                continue
            try:
                temp = int(temp)
            except:
                print("请输入合法罗马数字！")
                continue
            if temp < 0 or temp >= len(ordered_number): print("请输入合法罗马数字！")
            else:
                cancel_set.add(temp)
    else:
        for one in cancel_set.copy():
            if one not in ordered_number:
                log(f"cancel orderno error {one} not in {ordered_number}")
                logout(session)
                exit(-1)
            cancel_set.add(ordered_number.index(one))
            cancel_set.remove(one)


    for i in cancel_set:
        data = {
            'orderno': ordered_number[i]
        }
        res = session.post(url, data=data, headers=get_fake_headers())
        res = res.json()
        if res['returncode'] == 'SUCCESS':
            log(f'cancel orderno {ordered_number[i]}  {ordered_time[i]} successfully')

def weixin_push(content):
    url = "https://chizuo.top/api/push_msg_to_wx"
    account_id = '990731'
    account_password = 'chizuo'
    touser = 'oY7y153iUMRbMkdLw0Coysq8yxgU'
    data = {
        'account_id': account_id,
        'account_password': account_password,
        'content': content,
        'touser': touser,
    }
    res = requests.post(url, data=data)
    print(res.status_code, res.text)



class OrderBather():
    def __init__(self, session:requests.Session):
        self.base_time = timedelta(hours=14, minutes=30)
        self.available_order_list = []
        self.session = session
        self.ready_bath = None
        self.candidates = []
        self.init_candidate_time()

    def flush_available_order_list(self):
        self.available_order_list:list = available_order_list(self.session, config_account, config_appointdate)
        now = datetime.now()
        now = timedelta(hours=now.hour, minutes=now.minute+21)
        self.available_order_list = list(filter(lambda x: x['msg'] > 0 and x['end'] >= now and x['choise'] != '0',
                                           self.available_order_list))
        if len(self.available_order_list) == 0:
            log('there is no available time interval for you to have a bash!')
            logout(self.session)
            exit(-1)

    def init_candidate_time(self):
        for one in config_candidate_time:
            self.candidates.append(timedelta(hours=float(one[:2]), minutes=float(one[3:])))
        log(f'init candidates successfully {config_candidate_time}')

    def start_order(self):
        while self.ready_bath == None:
            time.sleep(1)
            self.flush_available_order_list()
            for cc in self.candidates:
                available = list(filter(lambda x: cc >= x['start'] and cc < x['end'],
                                        self.available_order_list))
                if len(available) > 0:
                    self.ready_bath = available[0]
                    if order_bath(self.session, config_account, config_appointdate, self.ready_bath['id']):
                        break
                    else:
                        self.ready_bath = None
        log(f"have orderd bath {config_appointdate} {self.ready_bath['timeslot']}")
        weixin_push(f"{get_time()} 已帮您成功预约洗澡 {config_appointdate} {self.ready_bath['timeslot']}")


# cancel("2008311741509346086", '2', "2020-08-31 18:00-18:30")

if __name__ == '__main__':
    pass
    # session = login(config_account, config_password)

    # order_checker = OrderBather(session)
    # order_checker.start_order()
    # cancel_order(session)
    # logout(session)
