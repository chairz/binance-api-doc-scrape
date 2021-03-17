from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import telebot
import schedule, time, pytz
from datetime import datetime, timezone

URLs = {'spot':'https://binance-docs.github.io/apidocs/spot/en/#change-log','futures':'https://binance-docs.github.io/apidocs/futures/en/#change-log','delivery':'https://binance-docs.github.io/apidocs/delivery/en/#change-log'}
current_date = {'spot':'', 'futures':'', 'delivery':''}

'''
get the content of the change logs, content ends at the next date
'''
def get_current_content(webpage, latest_date_idx, trade_type):
	content = webpage[latest_date_idx] + ' ' + trade_type.upper()
	pattern = re.compile(r'\d{4}-\d{2}-\d{2}')
	for i in range(latest_date_idx + 1, len(webpage) - 1 , 1):
		if pattern.search(webpage[i]):
			break
		content += webpage[i] + '\n'
	return content

'''
Update latest date for future comparison
'''
def update_current_date(webpage, latest_date_idx, trade_type):
	is_updated = False
	if current_date[trade_type] == '':
		telebot.send_message("SCRAPER RESTARTED AND UPDATED!")
		current_date[trade_type] = webpage[latest_date_idx]
		is_updated = True

	if webpage[latest_date_idx] != current_date[trade_type]:
		telebot.send_message("NEW UPDATE DETECTED!")
		is_updated = True
		current_date[trade_type] = webpage[latest_date_idx]

	return is_updated

def check_updates(webpage, trade_type):
	webpage = webpage.split('\n')
	change_log_idx = -1

	'''
	find index of Change Log keyword, following line is the start of latest updates
	'''
	for i in range(len(webpage) - 1, -1, -1):
		if 'Change Log' in webpage[i]:
			change_log_idx = i
			break 
	if change_log_idx < 0:
		print(f'change_log_idx: {change_log_idx} is not found!')
		return

	latest_date_idx = change_log_idx + 1
	has_update = update_current_date(webpage, latest_date_idx, trade_type)
	if has_update:
		content = get_current_content(webpage, latest_date_idx, trade_type)
		print(content)
		telebot.send_message(content)

	print(current_date)

def run_scraper():
	telebot.send_message(f'RUNNING SCRAPER at {datetime.now(pytz.utc)}')
	for trade_type, URL in URLs.items():
		page = urlopen(URL)
		html = page.read().decode("utf-8")
		soup = BeautifulSoup(html, "html.parser")
		check_updates(soup.get_text(), trade_type)

def heartbeat_check():
	telebot.send_message(f'HEARTBEAT CHECK at {datetime.now(pytz.utc)}')

run_scraper() #run once before scheduled
schedule.every(2).hours.do(heartbeat_check)
schedule.every(4).hours.do(run_scraper)

while True:
	schedule.run_pending()
	time.sleep(1)






	