import requests
from tools import get_fake_headers, log, get_time, read_config_file
from datetime import datetime, timedelta
import re
import time


class Api():
    def __init__(self, config=read_config_file()):
        self.set_basic_args(config)
        self.session = self.login()

    def set_basic_args(self, config:dict):
        self.account = config['account']
        self.password = config['password']
        self.expected_day = config['day']
        self.expected_time = config['time']
        self.wx_id = config['wx_id']
        self.set_sex_args(config['sex'])

    def get_expected_year_month_day(self)->datetime:
        return datetime(year=int(self.expected_day[:4]), month=int(self.expected_day[5:7]),
                    day=int(self.expected_day[8:]), hour=0, minute=0)


    def set_sex_args(self, sex:str):
        if sex == 'male':
            self.goodsid = '14'
            self.sex = '1'
            self.bathroomid = '14'
            self.bathroomname = '二校男浴室',
            self.goodslogo = "http://59.67.246.90:8088/photo/0001/f7f4b326beff45a6a848a8b1c9b53b68.png"
        elif sex == 'female':
            self.goodsid = '16'
            self.sex = '0'
            self.bathroomid = '16'
            self.bathroomname = '二校女浴室'
            self.goodslogo = "http://59.67.246.90:8088/photo/0001/2b86aeca7bae4906bf5906f91f4d216f.png"

    def login(self)->requests.Session:
        url = "http://bdhq.ncepu.edu.cn/ncepucenter/weixinlogin.json"
        session = requests.Session()
        data = {
            'reg_name': self.account,
            'password': self.password,
        }
        res = session.post(url, data=data, headers=get_fake_headers())
        if res.json()['success']:
            log(f"login {self.account} successfully")
            return session
        log(f"login {self.account} failed {res.text}")
        exit(-1)

    def logout(self):
        url = "http://bdhq.ncepu.edu.cn/ncepucenter/common_logout.t"
        res = self.session.get(url, headers=get_fake_headers())
        if res.status_code == 200:
            log("session logout successfully")
        else:
            log(f"session logout failed {res.text}")
            exit(-1)

    def order_homepage(self):
        order_show_url = f"http://yushiyuyue.ncepu.edu.cn/openHomePage?openid={self.account}"
        _ = self.session.get(order_show_url, headers=get_fake_headers())
        order_show_url = "http://yushiyuyue.ncepu.edu.cn/openHomePage"
        return self.session.get(order_show_url, headers=get_fake_headers())

    def available_order_list(self):
        if re.match("^\d{4}-\d{2}-\d{2}$", self.expected_day) == None:
            log(f"order_list {self.expected_day} format wrong!")
            exit(-1)
        if datetime(year=int(self.expected_day[:4]), month=int(self.expected_day[5:7]),
                    day=int(self.expected_day[8:]), hour=23, minute=59) < datetime.now():
            log(f"wrong datetime {self.expected_day}")
            return []
        _ = self.order_homepage()
        url = "http://yushiyuyue.ncepu.edu.cn/appointRules/queryAppointRules"
        data = {
            'goodsid': self.goodsid,
            'appointdate': self.expected_day
        }
        res = self.session.post(url, data=data, headers=get_fake_headers())
        # print(res.text)
        res = res.json()
        if res['returncode'] == 'SUCCESS':
            log('get order_list successfully')
            res = res['jsonArr']
            for one in res:
                start = one['timeslot'].split('-')
                end = start[1]
                start = start[0]
                day = self.get_expected_year_month_day()
                one['end'] = day.replace(hour=int(end[:2]), minute=int(end[3:]))
                one['start'] = day.replace(hour=int(start[:2]), minute=int(start[3:]))
                if one['msg'] == '已约满' or one['msg'] == '约满':
                    one['msg'] = 0
                else:
                    one['msg'] = int(one['msg'])
            return res
        else:
            log('get order_list failed')
            exit(-1)

    def ordered_bath_list(self):
        _ = self.order_homepage()
        url = "http://yushiyuyue.ncepu.edu.cn/openCustomerOrderList"
        res = self.session.get(url, headers=get_fake_headers())
        if res.status_code != 200:
            log(f"get ordered_bath_list failed {res.text}")
            self.logout()
            exit(-1)
        res = res.text
        ordered_number = re.findall("&quot;\d+&", res)
        ordered_number = [re.findall("\d+", x)[0] for x in ordered_number]
        ordered_time = re.findall("&quot;\d{4}-\d{2}-\d{2} \d{2}:\d{2}-\d{2}:\d{2}", res)
        ordered_time = [x[6:] for x in ordered_time]
        assert len(ordered_number) == len(ordered_time)
        return ordered_number, ordered_time

    def order_bath(self, rulesid):
        _ = self.available_order_list()
        data = {
            'bathroomid': self.bathroomid,
            'appointdate': self.expected_day,
            'rulesid': rulesid,
            'sex': self.sex,
            'goodslogo': self.goodslogo,
            'bathroomname': self.bathroomname,
        }
        order_url = "http://yushiyuyue.ncepu.edu.cn/appointmentGoods"
        res = self.session.post(order_url, data=data, headers=get_fake_headers())
        res = res.json()
        return res['returncode'] == 'SUCCESS'

    def cancel_order(self, cancel_set=None):
        assert isinstance(cancel_set, set) or cancel_set == None
        url = "http://yushiyuyue.ncepu.edu.cn/cancelGoodsOrder"
        ordered_number, ordered_time = self.ordered_bath_list()
        if len(ordered_number) == 0:
            log("当前未查询到已预约记录，请检查")
            self.logout()
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
                if one not in ordered_time:
                    log(f"cancel orderno error {one} not in {ordered_time}")
                    self.logout()
                    exit(-1)
                cancel_set.add(ordered_time.index(one))
                cancel_set.remove(one)

        for i in cancel_set:
            data = {
                'orderno': ordered_number[i]
            }
            res = self.session.post(url, data=data, headers=get_fake_headers())
            res = res.json()
            if res['returncode'] == 'SUCCESS':
                log(f'cancel orderno {ordered_number[i]}  {ordered_time[i]} successfully')
                return True
            log(f'cancel orderno {ordered_number[i]}  {ordered_time[i]} failed')
            return False

    def wechat_push(self, content):
        if self.wx_id == None:
            log('微信推送服务wx_id尚未配置，微信通知推送失败')
            return None
        url = "https://chizuo.top/api/wx_push_templete_to_user"
        account_id = '990731'
        account_password = 'chizuo'
        touser = self.wx_id
        data = {
            'account_id': account_id,
            'account_password': account_password,
            'content': content,
            'touser': touser,
            'title': '华电洗澡预约助手'
        }
        res = requests.post(url, data=data)
        log(f'微信推送 {res.status_code} {res.text}')




class OrderBather():
    def __init__(self, api:Api):
        self.base_time = timedelta(hours=14, minutes=30)
        self.available_order_list = []
        self.api = api
        self.session = api.session
        self.ready_bath = None
        self.candidates = []
        self.priority = 999
        self.init_candidate_time()

    def init_candidate_time(self):
        day = self.api.get_expected_year_month_day()
        for one in self.api.expected_time:
            self.candidates.append(day.replace(hour=int(one[:2]), minute=int(one[3:])))
        log(f'init candidates successfully {self.api.expected_day} {self.api.expected_time}')
        _, ordered_time = self.api.ordered_bath_list()
        for one in ordered_time:
            if one.find(self.api.expected_day) != -1:
                temp = {'timeslot': one[11:]}
                start = one[11:].split('-')
                end = start[1]
                start = start[0]
                temp['end'] = day.replace(hour=int(end[:2]), minute=int(end[3:]))
                temp['start'] = day.replace(hour=int(start[:2]), minute=int(start[3:]))
                self.ready_bath = temp
                break

        if self.ready_bath:
            for i, x in enumerate(self.candidates):
                if x >= self.ready_bath['start'] and x < self.ready_bath['end']:
                    self.priority = i
                    break
            log(f"have queried ordered bath {self.api.expected_day} {self.ready_bath['timeslot']}")

    def flush_available_order_list(self):
        self.available_order_list:list = self.api.available_order_list()
        self.available_order_list = list(filter(lambda x: x['msg'] > 0  and x['choise'] != '0',
                                           self.available_order_list))

    def start_order(self, ddl:datetime):
        log(f"开始帮您预约洗澡直到{get_time(ddl)}, 预约日期为{self.api.expected_day}, "
            f"期望时间为{self.api.expected_time}"
            f"您可随时按Ctrl + C结束此程序")
        while True:
            time.sleep(3)
            now = datetime.now()
            if self.priority == 0:
                break
            if now > ddl:
                break
            if self.ready_bath and now > (self.ready_bath['end'] - timedelta(minutes=20.0)):
                break
            self.flush_available_order_list()
            for pr, cc in enumerate(self.candidates):
                if self.priority < pr: continue
                available = list(filter(lambda x: cc >= x['start'] and cc < x['end'], self.available_order_list))
                if len(available) > 0:
                    if self.ready_bath:
                        temp = set()
                        temp.add(f"{self.api.expected_day} {self.ready_bath['timeslot']}")
                        if not self.api.cancel_order(cancel_set=temp):
                            continue
                        self.priority = 999
                    if not self.api.order_bath(available[0]['id']):
                        continue
                    self.ready_bath = available[0]
                    self.priority = pr

        if self.ready_bath:
            log(f"have orderd bath {self.api.expected_day} {self.ready_bath['timeslot']}")
            self.api.wechat_push(f"账号 {self.api.account} 成功预约洗澡 {self.api.expected_day} {self.ready_bath['timeslot']}")
        else:
            log(f"sorry have not ordered any time {self.api.expected_day} {self.api.expected_time}")
            self.api.wechat_push(f"账号 {self.api.account} 预约失败，脚本已自动结束，未能帮您在 {self.api.expected_day} {self.api.expected_time} 成功预约")
            self.api.logout()
            exit(0)




if __name__ == '__main__':
    pass