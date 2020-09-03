from api import ordered_bath_list, login, logout, OrderBather, cancel_order, available_order_list
from config import *
from datetime import datetime, timedelta
from tools import log
import time


def check_config():
    now = datetime.now()
    end = now + timedelta(days=3)
    end = end.replace(hour=22, minute=9, second=50)
    for one in config_candidate_time:
        t = datetime(year=int(config_appointdate[:4]), month=int(config_appointdate[5:7]),
                     day=int(config_appointdate[8:]), hour=int(one[:2]), minute=int(one[3:]))
        if not (t >= now and t <= end):
            print("请检查config.py中的日期时间设置！")
            exit(-1)

check_config()
session = login(config_account, config_password)
bather = OrderBather(session)

def main(x:int):
    if x == 0:
        order_list = available_order_list(session, config_account, config_appointdate)
        for i, one in enumerate(order_list):
            suffix = '不可预约' if one['choise'] == '0' else '可预约'
            print(f'编号：{i}', config_appointdate, one['timeslot'], f"剩余{one['msg']}", suffix)
    elif x == 1:
        bather.start_order()
    elif x == 2:
        ordered_number, ordered_time = ordered_bath_list(session)
        if len(ordered_number) == 0:
            log("当前未查询到已预约记录，请检查")
            logout(session)
            exit(-1)
        print(f"已预约编号如下，共{len(ordered_number)}个")
        for i in range(len(ordered_number)):
            print(f"编号：{i}  预约时间：{ordered_time[i]}")
    elif x == 3:
        cancel_order(session)


def show_tip():
    time.sleep(1.2)
    tip = "\n\n请输入编号，进行功能选择，请务必确保config.py文件中的配置正确！"
    print(tip)
    choices = [
        f'查看{config_appointdate}可预约的洗澡时间段',
        f'按照配置{config_appointdate} {config_candidate_time}进行预约洗澡',
        '查看已经预约的列表',
        '取消预约',
        '退出'
    ]
    for i in range(len(choices)):
        print(f"编号：{i}  {choices[i]}")
    while True:
        x = input()
        try:
            x = int(x)
            assert x >= 0 and x < len(choices)
        except:
            print("请输入正确编号")
            continue
        break
    return x


if __name__ == '__main__':
    while True:
        try:
            x = show_tip()
            if x == 4:
                logout(session)
                break
            main(x)
        except:
            logout(session)

