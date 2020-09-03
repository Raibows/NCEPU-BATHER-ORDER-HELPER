from tools import log, check_config, read_config_file
import time
from datetime import datetime
from api import Api, OrderBather


config = read_config_file()
api = Api(config)
bather = OrderBather(api)


def main(x:int):
    if x == 0:
        order_list = api.available_order_list()
        for i, one in enumerate(order_list):
            suffix = '不可预约' if (one['choise'] == '0' or one['msg'] == 0) else '可预约'
            print(f'编号：{i}', config['day'], one['timeslot'], f"剩余{one['msg']}", suffix)
    elif x == 1:
        if config['ddl'] == None: ddl = max(config['time'])
        else: ddl = config['ddl']
        bather.start_order(datetime.now().replace(hour=int(ddl[:2]), minute=int(ddl[3:])))
    elif x == 2:
        ordered_number, ordered_time = api.ordered_bath_list()
        if len(ordered_number) == 0:
            log("当前未查询到已预约记录，请检查")
            return None
        print(f"已预约编号如下，共{len(ordered_number)}个")
        for i in range(len(ordered_number)):
            print(f"编号：{i}  预约时间：{ordered_time[i]}")
    elif x == 3:
        api.cancel_order(cancel_set=None)


def show_tip():
    time.sleep(1.2)
    tip = "\n\n请输入编号，进行功能选择，请务必确保config.py文件中的配置正确！"
    print(tip)
    choices = [
        f"查看{config['day']}可预约的洗澡时间段",
        f"按照配置{config['day']} {config['time']}进行预约洗澡",
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
                api.logout()
                break
            main(x)
        except:
            api.logout()

