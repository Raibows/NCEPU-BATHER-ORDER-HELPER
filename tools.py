from fake_headers import Headers
from datetime import datetime, timedelta
import sys

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

def get_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == '__main__':
    print(get_time())
