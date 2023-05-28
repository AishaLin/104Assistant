from datetime import datetime
import pytz
from telegram_bot import Telegram_Bot
from slack_bot import Slack_Bot
from proxy104 import Proxy104
from proxySoarCloud import ProxySoarCloud
import time
import os
from constants import NATIONAL_HOLIDAYS, WORK_HOUR_START, WORK_HOUR_END, APP__104

class Assistant:
  def __init__(self):
    self.app = os.getenv('APP')
    self.proxy = Proxy104() if self.app == APP__104 else ProxySoarCloud()
    self.telegram_bot = Telegram_Bot()
    self.slack_bot = Slack_Bot()
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

  def check_is_OoO(self, today):
    try:
      hasInProgressRequestForm, hasInProgressWithdrawForm = self.proxy.check_today_OoO_in_progress_status(today)
    except Exception as error:
      self.bot_send_message(f'GET IN PROGRESS OoO FORM LIST FAIL!! {error}')
    try:
      hasFinishedRequestForm, hasFinishedWithdrawForm = self.proxy.check_today_OoO_finished_status(today)
    except Exception as error:
      self.bot_send_message(f'GET FINISHED OoO FORM LIST FAIL!! {error}')
    return hasInProgressRequestForm or (hasFinishedRequestForm and not hasFinishedWithdrawForm and not hasInProgressRequestForm and not hasInProgressWithdrawForm)

  def check_is_workday(self, date):
    is_OoO = self.check_is_OoO(date)
    return date.weekday() < 5 and date not in NATIONAL_HOLIDAYS and not is_OoO

  def get_now_tw(self):
    now_utc = datetime.now(pytz.utc)
    return now_utc.astimezone(self.taiwan_tz)
  
  def login(self, time):
    try:
      self.proxy.login()
      print('login successfully!!', time.strftime("%Y/%m/%d %a %H:%M:%S"))
    except Exception as error:
      self.bot_send_message(f'LOGIN FAIL!! {error}')

  def handle_check_in_out(self, time, is_check_in_type):
    try:
      self.proxy.check_in_out(is_check_in_type)
      if is_check_in_type:
        self.bot_send_message(f'check in at {time.strftime("%Y/%m/%d %a %H:%M:%S")}')
        self.check_in_time = time.strftime("%Y/%m/%d %H:%M:%S")
      else:
        self.bot_send_message(f'check out at {time.strftime("%Y/%m/%d %a %H:%M:%S")}')
        self.check_in_time = ''
    except Exception as error:
      self.bot_send_message(f'CHECK IN FAIL!! {error}')

  def check_is_work_enough(self, now_tw):
    if self.check_in_time == '':
      return True
    try:
      check_in = datetime.strptime(self.check_in_time, '%Y/%m/%d %H:%M:%S')
      current = datetime.strptime(now_tw.strftime('%Y/%m/%d %H:%M:%S'), '%Y/%m/%d %H:%M:%S')
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
    self.bot_send_message(f'Hi, your {self.app} check-in bot has started work at {self.get_now_tw().strftime("%Y/%m/%d %a %H:%M:%S")}')
    while True:
      try:
        self.check_in_out_if_necessary()
      except:
        self.bot_send_message('What the (☉д⊙)"')
      time.sleep(300)

if __name__ == '__main__':
  try:
    assistant = Assistant()
    assistant.main()
  except Exception as error:
    assistant.bot_send_message(f'SOMETHING WRONG!! {error}')
