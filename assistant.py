from datetime import datetime, date, timedelta
import pytz
from telegram_bot import Telegram_Bot
from slack_bot import Slack_Bot
from client104 import Client104
import time
import os
from constants import NATIONAL_HOLIDAYS, FORM_CODE__OOO_REQUEST, FORM_CODE__OOO_WITHDRAW, REQUEST_STATUS__COMPLETED, WORK_HOUR_START, WORK_HOUR_END

class Assistant:
  def __init__(self):
    self.telegram_bot = Telegram_Bot()
    self.slack_bot = Slack_Bot()
    self.client104 = Client104()
    self.taiwan_tz = pytz.timezone('Asia/Taipei')
    now_tw_hour = self.get_now_tw().hour
    self.is_working = now_tw_hour >= WORK_HOUR_START and now_tw_hour <= WORK_HOUR_END
    self.check_in_time = ''

  def bot_send_message(self, msg):
    print(msg)
    if os.getenv('TELEGRAM_BOT_TOKEN') and os.getenv('TELEGRAM_CHAT_ID'):
      acc = os.getenv('ACC')
      user_name = acc.split('@')[0]
      self.telegram_bot.send_msg(f'[{user_name.upper()}] {msg}')
    if os.getenv('SLACK_WEBHOOK_URL'):
      self.slack_bot.send_msg(msg)
    

  def convert_date_str_to_datetime(self, date_str):
    date_parts = date_str.split('/')
    if len(date_parts) < 3:
      return None
    year = int(date_parts[0])
    month = int(date_parts[1])
    day = int(date_parts[2])
    return date(year, month, day)

  def parse_summary_text_to_date_list(self, summary_text):
    start_date_str = summary_text.split(' ')[0]
    start_date = self.convert_date_str_to_datetime(start_date_str)
    end_date_str = summary_text.split('~ ')[1].split(' ')[0] if len(summary_text.split('~ ')) > 1 and len(summary_text.split('~ ')[1].split(' ')) > 0 else start_date_str
    end_date = self.convert_date_str_to_datetime(end_date_str) or start_date

    date_list = []
    delta = timedelta(days=1)
    current_date = start_date
    while current_date <= end_date:
      date_list.append(current_date)
      current_date += delta
    return date_list

  def get_OoO_date_list_from_forms(self, forms):
    OoO_list = set()
    for item in forms:
      summary_text = item['summary']
      OoO_list_per_form = self.parse_summary_text_to_date_list(summary_text)
      for OoO_date in OoO_list_per_form:
        OoO_list.add(OoO_date)
    return OoO_list
  
  def is_OoO_request_type(self, form):
    return form['formCode'] == FORM_CODE__OOO_REQUEST
  
  def is_OoO_withdraw_type(self, form):
    return form['formCode'] == FORM_CODE__OOO_WITHDRAW
  
  def is_sign_off_completed(self, form):
    return form['requestStatus'] == REQUEST_STATUS__COMPLETED

  def check_is_OoO(self, today):
    try:
      inProgressForms = self.client104.get_in_progress_form_list()
      inProgressOoORequestForms = filter(self.is_OoO_request_type, inProgressForms)
      inProgressOoOWithdrawForms = filter(self.is_OoO_withdraw_type, inProgressForms)
      inProgressOoORequestDateList = self.get_OoO_date_list_from_forms(inProgressOoORequestForms)
      inProgressOoOWithdrawDateList = self.get_OoO_date_list_from_forms(inProgressOoOWithdrawForms)
    except Exception as error:
      self.bot_send_message(f'GET IN PROGRESS OoO FORM LIST FAIL!! {error}')
    try:
      finishedForms = list(filter(self.is_sign_off_completed, self.client104.get_finished_form_list()))
      finishedOoORequestForms = filter(self.is_OoO_request_type, finishedForms)
      finishedOoOWithdrawForms = filter(self.is_OoO_withdraw_type, finishedForms)
      finishedOoORequestDateList = self.get_OoO_date_list_from_forms(finishedOoORequestForms)
      finishedOoOWithdrawDateList = self.get_OoO_date_list_from_forms(finishedOoOWithdrawForms)
    except Exception as error:
      self.bot_send_message(f'GET FINISHED OoO FORM LIST FAIL!! {error}')
    overallOoODateList = inProgressOoORequestDateList.union(finishedOoORequestDateList) - inProgressOoOWithdrawDateList - finishedOoOWithdrawDateList
    return today in overallOoODateList

  def check_is_workday(self, date):
    is_OoO = self.check_is_OoO(date)
    return date.weekday() < 5 and date not in NATIONAL_HOLIDAYS and not is_OoO

  def get_now_tw(self):
    now_utc = datetime.now(pytz.utc)
    return now_utc.astimezone(self.taiwan_tz)
  
  def login(self, time):
    try:
      self.client104.login()
      print('login successfully!!', time.strftime("%Y/%m/%d %a %H:%M:%S"))
    except Exception as error:
      self.bot_send_message(f'LOGIN FAIL!! {error}')

  def handle_check_in_out(self, time, is_check_in_type):
    try:
      self.client104.check_in()
      if is_check_in_type:
        self.bot_send_message(f'check in at {time.strftime("%Y/%m/%d %a %H:%M:%S")}')
        self.check_in_time = time.strftime("%Y/%m/%d %a %H:%M:%S")
      else:
        self.bot_send_message(f'check out at {time.strftime("%Y/%m/%d %a %H:%M:%S")}')
        self.check_in_time = ''
    except Exception as error:
      self.bot_send_message(f'CHECK IN FAIL!! {error}')

  def check_is_work_enough(self, now_tw):
    if self.check_in_time == '':
      return True
    try:
      check_in = datetime.strptime(self.check_in_time, '%Y-%m-%d %H:%M:%S')
      current = datetime.strptime(now_tw.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
      time_diff = current - check_in
      total_seconds = abs(time_diff.total_seconds())
      hours_diff = total_seconds / 3600
    except Exception as error:
      self.bot_send_message(f'CHECK IS WORK ENOUGH FAIL!! {error}')
    return hours_diff >= 9

  def check_in_out_if_necessary(self):
    now_tw = self.get_now_tw()
    self.login(now_tw)
    
    today_tw = now_tw.date()
    is_workday = self.check_is_workday(today_tw)
    is_work_enough = self.check_is_work_enough(now_tw)

    if is_workday:
      should_check_in = not self.is_working and now_tw.hour == WORK_HOUR_START
      should_check_out = self.is_working and now_tw.hour == WORK_HOUR_END and is_work_enough
      if should_check_in or should_check_out:
        self.handle_check_in_out(now_tw, should_check_in)
        self.is_working = not self.is_working
    
  def main(self):
    self.bot_send_message(f'Hi, your 104 assistant has started work at {self.get_now_tw().strftime("%Y/%m/%d %a %H:%M:%S")}')
    while True:
      try:
        self.check_in_out_if_necessary()
      except:
        self.bot_send_message('retry now.')
        continue
      time.sleep(300)

if __name__ == '__main__':
  try:
    assistant = Assistant()
    assistant.main()
  except Exception as error:
    assistant.bot_send_message(f'SOMETHING WRONG!! {error}')
