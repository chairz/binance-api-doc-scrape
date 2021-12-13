import os
import re
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen

import pytz
import schedule
import time
from bs4 import BeautifulSoup

import telebot

URLs = {'spot': 'https://binance-docs.github.io/apidocs/spot/en/#change-log',
        'futures': 'https://binance-docs.github.io/apidocs/futures/en/#change-log',
        'delivery': 'https://binance-docs.github.io/apidocs/delivery/en/#change-log'}

'''
get the content of the change logs, content ends at the next date
'''


def get_current_content(webpage, latest_date_idx, trade_type):
    content = webpage[latest_date_idx] + ' ' + trade_type.upper()
    pattern = re.compile(r'\d{4}-\d{2}-\d{2}')
    for i in range(latest_date_idx + 1, len(webpage) - 1, 1):
        if pattern.search(webpage[i]):
            break
        content += webpage[i] + '\n'
    return content


'''
Update and compare current content with past content from a txt file
'''


def update_change_log(content, trade_type):
    has_update = False
    Path('log').mkdir(parents=True, exist_ok=True)
    file_path = f'log/{trade_type}.txt'

    if not os.path.exists(file_path):
        f = open(file_path, "w")
        f.write(content)
        f.close()
        has_update = True

    file_reader = open(file_path, "r")

    if content != file_reader.read():
        file_writer = open(file_path, "w")
        file_writer.write(content)
        file_writer.close()
        has_update = True

    return has_update


def check_updates(webpage, trade_type):
    webpage = webpage.split('\n')
    change_log_idx = -1

    for i in range(len(webpage) - 1, -1,
                   -1):  # find index of Change Log keyword, following line is the start of latest updates
        if 'Change Log' in webpage[i]:
            change_log_idx = i
            break
    if change_log_idx < 0:
        print(f'change_log_idx: {change_log_idx} is not found!')
        return

    latest_date_idx = change_log_idx + 1
    content = get_current_content(webpage, latest_date_idx, trade_type)
    has_update = update_change_log(content, trade_type)
    if has_update:
        telebot.send_message(content)


def run_scraper():
    for trade_type, URL in URLs.items():
        page = urlopen(URL)
        html = page.read().decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        check_updates(soup.get_text(), trade_type)


def heartbeat_check():
    telebot.send_check_message(f'HEARTBEAT CHECK at {datetime.now(pytz.utc)}')


schedule.every(15).minutes.do(run_scraper)
schedule.every(4).hours.do(heartbeat_check)


while True:
    schedule.run_pending()
    time.sleep(1)
