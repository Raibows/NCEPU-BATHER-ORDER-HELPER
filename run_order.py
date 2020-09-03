from tools import log, regex_datetime_format, get_time, read_config_file
import argparse
from datetime import datetime, timedelta
from api import Api, OrderBather



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    today = datetime.now().strftime("%Y-%m-%d")
    parser.add_argument('--day', default=today, type=regex_datetime_format,
                        help=f'请输入形如{today}这样的日期格式，默认为今天')
    parser.add_argument('--time', nargs='+',
                        help=f'请输入你想要预约的洗澡时间，可以输入多个形如18:03格式的时间，最前面的优先级最高')
    parser.add_argument('--ddl', default=None,
                        help='请输入截止脚本时间，如若超出ddl形如18:03，则脚本自动停止，默认为22:10或time时间中最晚一个')
    args = parser.parse_args()
    expected_day = args.day
    expected_time = args.time
    ddl = args.ddl
    if ddl == None:
        ddl = max(expected_time)
    config = read_config_file()
    config['day'] = expected_day
    config['time'] = expected_time
    config['ddl'] = ddl
    ddl = datetime.now().replace(hour=int(ddl[:2]), minute=int(ddl[3:]))

    api = Api(config)
    bather = OrderBather(api)
    bather.start_order(ddl)




