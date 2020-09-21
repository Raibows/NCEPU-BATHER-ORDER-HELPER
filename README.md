## NCEPU BATHER ORDER HELPER 华电洗澡预约助手

### 须知

此脚本仅供方便电脑端用户、个人测试以及学习用途使用，其他用途严格禁止。本项目遵循GPLv3协议。目前适用于华电保定二校区使用。如您有bug反馈或改进，欢迎issue，欢迎pull requests。点个star当然更欢迎啦！😁😁

### 功能简述

1. 预约洗澡：候补洗澡，实时监控余量下单预约，多时间段保障
2. 查看余量：查看任意日期，所有时间段余量
3. 取消预约：查看已预约列表，选择取消预约

### 环境准备

1. 请确保运行环境中有python，且version >= 3.7
2. 将项目克隆至本地``git clone https://github.com/Raibows/NCEPU-BATHER-ORDER-HELPER``
3. 强烈建议您为本项目创建一个虚拟环境，可使用``python -m venv venv``
4. 激活虚拟环境后，安装依赖``pip install -r requirements.txt``

### 交互型使用

1. 当您第一次使用时``python main.py``，会自动生成``config.json``文件，作为本项目的配置文件
2. 请按照``config.json``中的提示填写完善信息，参数不明确的可见本页最后，或在本项目中提出issue寻求帮助
3. 完善后，再次运行``python main.py``，根据相应提示进行各种功能操作即可

### 部署型使用

1. 请先使用``python main.py``，自动生成``config.json``文件，作为本项目的配置文件  
2. 完善``config.json``文件中的``account``、``password``、``sex``字段
3. 运行``python run_order.py -h``查看参数帮助，按照自己的需求填写相应的参数
   例如我想要在明天，[21:30, 18:40, 14:45]这三个时间段其中之一去洗澡（且优先级依次递减），那么命令应该是

   ```bash
   python run_order.py --day 1 --time 21:30 18:40 14:45
   ```
   
   其中``--day 1``参数使用了魔术方法，即0代表今天，1代表明天，以此类推；你也可以使用形如``--day 2020-09-06``这样的参数。上面的命令没有指定``--ddl``参数，那么将使用默认值，即无论是否预约成功，将在``明天 max(21:30, 18:40, 14:45) - 1hour``，即明天20:30时结束，详细解释可看下面参数字段中的``ddl``

### 配置文件参数详解

1. ``account``：即学号
2. ``password``：华电微后勤公众号的登录密码
3. ``sex``：性别，为（male，female）之一
4. ``day``：预约的日期，例如2020-09-05，正则表达式匹配``^\d{4}-\d{2}-\d{2}$``
5. ``time``：期望的时间列表，例如[21:30, 18:40, 14:45]这三个时间段之一；越在前面优先级越高，程序会努力尽可能预约到优先级最高的，这意味着即使已经预约到了时间段其中之一，也不会立即停止运行，而是继续候补优先级更高的时间段。建议配合``ddl``参数确定最迟微信通知/程序结束时间
6. ``ddl``：无论是否预约到，均在ddl时刻停止程序运行。默认值：``在day日期，max(time)时刻 - 1hour``时刻停止运行；自行指定一个时刻如``22:10``将在``脚本运行日期，22:10``时刻停止运行；也可以给出符合正则表达式``^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$``时间格式以满足其他日期时间，例如``2020-09-22 22:10``
7. ``wx_id``：即微信个人的openid，此项默认值为null；扫描以下二维码关注公众号或回复任意字符，即可获得个人的``wx_id``；此后预约结果将通过此微信公众号给您发送提醒；也可使用自己的通知服务，更改``api.py``文件下的``Api/wechat_push``函数即可
<div align=center>
   <img src="https://raw.githubusercontent.com/Raibows/MarkdownPhotos/master/picgoimage/20200908210607.png" alt="pic09-08-21-05-16" style="zoom: 40%;" />
</div>