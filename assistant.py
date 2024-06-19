from datetime import datetime
import pytz
from telegram_bot import Telegram_Bot
from slack_bot import Slack_Bot
from proxy104 import Proxy104
from proxySoarCloud import ProxySoarCloud
import time
from constants import NATIONAL_HOLIDAYS, APP__104, APP__SOAR_CLOUD
from config import user_list, APP
from user import User
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
import random

class Assistant:
  def __init__(self):
    self.app = APP
    self.proxy = Proxy104() if self.app == APP__104 else ProxySoarCloud()
    self.telegram_bot = Telegram_Bot()
    self.slack_bot = Slack_Bot()
    self.taiwan_tz = pytz.timezone('Asia/Taipei')


  def bot_send_message(self, msg, user):
    print(msg)
    if not user:
      self.telegram_bot.send_msg(msg)
      return
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
      if self.app == APP__104:
        acc = user.account
        user_name = acc.split('@')[0]
        self.telegram_bot.send_msg(f'[{user_name.upper()}] {msg}')
      if self.app == APP__SOAR_CLOUD:
        user_name = user.name
        user_id = user.account
        self.telegram_bot.send_msg(f'[{user_id} | {user_name}] {msg}')
    if user.slack_webhook_url:
      self.slack_bot.send_msg(user.slack_webhook_url, msg)


  def check_is_OoO(self, today, user_name, user_account, user_sessionGuid):
    try:
      hasInProgressRequestForm, hasInProgressWithdrawForm = self.proxy.check_today_OoO_in_progress_status(today)
    except Exception as error:
      self.bot_send_message(f'{user_name} | failed to retrieve the in-progress OoO form list!! {error}', None)
    try:
      hasFinishedRequestForm, hasFinishedWithdrawForm = self.proxy.check_today_OoO_finished_status(today, user_account, user_sessionGuid)
      return hasInProgressRequestForm or (hasFinishedRequestForm and not hasFinishedWithdrawForm and not hasInProgressRequestForm and not hasInProgressWithdrawForm)
    except Exception as error:
      self.bot_send_message(f'{user_name} | failed to retrieve the finished OoO form list!! {error}', None)
      return False


  def check_is_workday(self, date, user_name, user_account, user_sessionGuid):
    is_OoO = self.check_is_OoO(date, user_name, user_account, user_sessionGuid)
    return date.weekday() < 5 and date not in NATIONAL_HOLIDAYS and not is_OoO


  def get_now_tw(self):
    now_utc = datetime.now(pytz.utc)
    return now_utc.astimezone(self.taiwan_tz)


  def login(self, time, user_name, user_account, user_password):
    try:
      user_sessionGuid = self.proxy.login(user_account, user_password)
      print(f'{user_name} login successfully!!', time.strftime("%Y/%m/%d %a %H:%M:%S"))
      return user_sessionGuid
    except Exception as error:
      self.bot_send_message(f'{user_name} login fail!! {error}', None)


  def handle_check_in_out(self, time, is_check_in_type, user):
    try:
      self.proxy.check_in_out(is_check_in_type, user.sessionGuid)
      if is_check_in_type:
        self.bot_send_message(f'check-in at {time.strftime("%Y/%m/%d %a %H:%M:%S")}', user)
      else:
        self.bot_send_message(f'check-out at {time.strftime("%Y/%m/%d %a %H:%M:%S")}', user)
    except Exception as error:
      self.bot_send_message(f'check-in fail!! {error}', user)


  def check_in_out_if_necessary(self, user):
    now_tw = self.get_now_tw()
    should_check_in = user.is_workday and now_tw.hour < 12
    should_check_out = user.is_workday and now_tw.hour > 12

    if should_check_in or should_check_out:
      self.handle_check_in_out(now_tw, should_check_in, user)
    else:
      self.bot_send_message(f'*٩(◕‿◕｡)۶✿ﾟ‘ﾟ･.｡✧ Yippee!*', user)


  def random_sleep(self, min_s, max_s):
    random_int = random.randint(min_s, max_s)
    time.sleep(random_int)


  def create_users(self):
    users = []
    random.shuffle(user_list)
    for user in user_list:
      now_tw = self.get_now_tw()
      today_tw = now_tw.date()
      user_sessionGuid = self.login(now_tw, user['NAME'], user['ACC'], user['PPP'])
      is_workday = self.check_is_workday(today_tw, user['NAME'], user['ACC'], user_sessionGuid)
      users.append(User(user['ACC'], user['PPP'], user['NAME'], is_workday, user_sessionGuid, user['SLACK_WEBHOOK_URL']))
      self.random_sleep(0, 10)
    return users


  def main(self):
    self.bot_send_message(f'Hi, your {self.app} check-in bot started working at {self.get_now_tw().strftime("%Y/%m/%d %a %H:%M:%S")}', None)
    users = self.create_users()

    for user in users:
      try:
        self.random_sleep(5, 50)
        self.check_in_out_if_necessary(user)
      except Exception as e:
        print(e)
        self.bot_send_message(f'What the (☉д⊙)", {e}', user)


if __name__ == '__main__':
  try:
    assistant = Assistant()
    assistant.main()
  except Exception as error:
    assistant.bot_send_message(f'Something wrong!! {error}', None)
