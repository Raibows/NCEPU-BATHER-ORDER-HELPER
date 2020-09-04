## NCEPU BATHER ORDER HELPER 华电洗澡预约助手

### 须知

此脚本仅供方便电脑端用户、个人测试以及学习用途使用，其他用途严格禁止。本项目遵循GPLv3协议。目前适用于华电保定二校区使用。如您有bug反馈或改进，欢迎issue，欢迎pull requests。点个star当然更欢迎啦！😁😁

### 功能简述

1. 预约洗澡（候补洗澡，实时监控余量下单预约）
2. 查看余量
3. 取消预约

### 环境准备

1. 请确保运行环境中有python，version >= 3.7
2. 将项目克隆至本地``git clone https://github.com/Raibows/NCEPU-BATHER-ORDER-HELPER``
3. 强烈建议您为本项目创建一个虚拟环境，可使用``python -m venv venv``
4. 激活虚拟环境后，安装依赖``pip install -r requirements.txt``

### 交互型使用

1. 当您第一次使用时``python main.py``，会自动生成``config.json``文件，作为本项目的配置文件
2. 请按照``config.json``中的提示填写完善信息，参数不明确的可见本页最后，或在本项目中提出issue
3. 完善后，再次运行``python main.py``，根据相应提示进行各种功能操作即可

### 部署型使用

1. 请先使用``python main.py``，生成``config.json``文件，作为本项目的配置文件

2. 完善``config.json``文件中的``account``、``password``、``sex``字段即可

3. 运行``python run_order.py -h``查看参数帮助，按照自己的需求填写相应的参数

   例如我想要在明天，[21:30, 18:40, 14:45]这三个时间段其中之一去洗澡（且优先级依次递减），那么命令应该是

   ```bash
   python run_order.py --day 1 --time 21:30 18:40 14:45
   ```

   该脚本无论是否预约成功，将在``明天 21:30 - 1hour``，即明天20:30时结束，可自行设定ddl参数。

### 配置文件参数详解

1. account：即学号
2. password：华电微后勤公众号的登录密码
3. sex：性别，为（male，female）之一
4. day：预约的日期，例如2020-09-05，正则表达式匹配``^\d{4}-\d{2}-\d{2}$``
5. time：期望的时间列表，越在前面优先级越高，例如[21:30, 18:40, 14:45]这三个时间段之一
6. ddl：无论是否预约到，均在ddl时刻停止程序运行。默认值：``在day日期，max(time)时刻 - 1hour``时刻停止运行；自行指定一个时刻如``22:10``将``在day日期，22:10``时刻停止运行

另外请注意，微信通知尚未完善，将被禁用，您可自行完善``./api.py``中的``weixin_push``函数。

