from fake_headers import Headers
from datetime import datetime, timedelta
import argparse
import re
import json
import os

headers = None

def get_fake_headers():
    global headers
    if headers: return headers
    headers = Headers(os='mac', headers=True, browser='Chrome')
    headers = headers.generate()
    return headers

def log(msg:str):
    time = datetime.now().strftime("%H:%M:%S")
    print(f"{time} {msg}")

def get_time(time:datetime=None):
    if time:
        return time.strftime("%Y-%m-%d %H:%M:%S")
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def check_config(day, candidate_time):
    now = datetime.now()
    end = now + timedelta(days=3)
    end = end.replace(hour=22, minute=9, second=50)
    for one in candidate_time:
        t = datetime(year=int(day[:4]), month=int(day[5:7]),
                     day=int(day[8:]), hour=int(one[:2]), minute=int(one[3:]))
        if not (t >= now and t <= end):
            print("请检查config.py中的日期时间设置！")
            exit(-1)

def regex_datetime_format(val:str):
    if not isinstance(val, str):
        raise TypeError
    pat = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    if not pat.match(val):
        try:
            val = int(val)
            assert val < 3
        except:
            raise argparse.ArgumentTypeError
    else:
        return val
    val = datetime.now() + timedelta(days=val)
    return val.strftime("%Y-%m-%d")

def read_config_file(path=r'./config.json'):
    if not os.path.exists(path):
        config = {
            "account": "学号",
            "password": "华电微后勤的密码",
            "day": "例如2020-09-04",
            "time":
                [
                    "14:15",
                    "18:03",
                    "越在上面优先级越高"
                ],
            "ddl": '脚本强制结束时间，也就是最晚期望得到结果的时间，无论抢没抢到，例如22:10，则在今天22:10结束；默认为null，则在'
                   '您设定的日期，time列表最后一个期望时间，提前1小时结束',
            "sex": '请选择（male，female）之一',
            "wx_id": None
        }
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(config, file, ensure_ascii=False, indent=4, sort_keys=True)
            log('已帮您生成config.json配置文件，请先修改配置文件再运行该脚本')
            exit(0)
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)

def get_ddl(expected_day, ddl, time:list)->datetime:
    time = max(time)
    if ddl != None:
        pat = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$")
        if pat.match(ddl):
            ddl = datetime.strptime(ddl, "%Y-%m-%d %H:%M")
        else:
            pat = re.compile(r"^\d{2}:\d{2}$")
            if pat.match(ddl):
                ddl = datetime.now().replace(hour=int(ddl[:2]), minute=int(ddl[3:]))
            else:
                log(f'wrong ddl time format {ddl}')
                exit(-1)
    order_last = datetime(year=int(expected_day[:4]), month=int(expected_day[5:7]),
             day=int(expected_day[8:]), hour=int(time[:2]), minute=int(time[3:]))
    if ddl == None or ddl > order_last:
        return order_last - timedelta(hours=1)
    return ddl


if __name__ == '__main__':
    print(read_config_file())
