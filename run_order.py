from tools import log, regex_datetime_format, get_time, read_config_file, get_ddl
import argparse
from datetime import datetime, timedelta
from api import Api, OrderBather



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    today = datetime.now().strftime("%Y-%m-%d")
    parser.add_argument('--day', default=today, type=regex_datetime_format,
                        help=f'请输入形如{today}这样的日期格式，默认为今天；或者输入0，1，2，3等，0代表今天，1代表明天，以此类推')
    parser.add_argument('--time', nargs='+',
                        help=f'请输入你想要预约的洗澡时间，可以输入多个形如18:03格式的时间，最前面的优先级最高')
    parser.add_argument('--ddl', default=None,
                        help='请输入截止脚本时间，具体格式请参考README.md')
    args = parser.parse_args()
    expected_day = args.day
    expected_time = args.time
    ddl = args.ddl
    ddl = get_ddl(expected_day, ddl, expected_time)
    config = read_config_file()
    config['day'] = expected_day
    config['time'] = expected_time
    config['ddl'] = ddl


    api = Api(config)
    bather = OrderBather(api)
    bather.start_order(ddl)




