from datetime import datetime, date, timedelta
import pytz
from telegram_bot import Telegram_Bot
from client104 import Client104
import time

class Assistant:
  def __init__(self):
    self.bot = Telegram_Bot()
    self.client104 = Client104()
    self.taiwan_tz = pytz.timezone('Asia/Taipei')
    self.national_holidays = set([
      date(2023, 2, 27),
      date(2023, 2, 28),
      date(2023, 4, 3),
      date(2023, 4, 4),
      date(2023, 4, 5),
      date(2023, 5, 1),
      date(2023, 6, 22),
      date(2023, 6, 23),
      date(2023, 9, 29),
      date(2023, 10, 9),
      date(2023, 10, 10),
      date(2024, 1, 1),
    ])

  def bot_send_message(self, msg):
    self.bot.send_msg(msg)
    print(msg)

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
  
  def check_is_OoO(self, today):
    inProgressForms = self.client104.get_in_progress_OoO_form_list()
    inProgressOoODateList = self.get_OoO_date_list_from_forms(inProgressForms)
    finishedForms = self.client104.get_finished_OoO_form_list()
    finishedOoODateList = self.get_OoO_date_list_from_forms(finishedForms)
    overallOoODateList = inProgressOoODateList.union(finishedOoODateList)
    return today in overallOoODateList

  def check_is_workday(self, date):
    is_OoO = self.check_is_OoO(date)
    return date.weekday() < 5 and date not in self.national_holidays and not is_OoO

  def get_now_tw(self):
    now_utc = datetime.now(pytz.utc)
    return now_utc.astimezone(self.taiwan_tz)
  
  def login(self, time):
    try:
      self.client104.login()
      print('login successfully!!', time.strftime("%Y/%m/%d %a %H:%M:%S"))
    except Exception as error:
      self.bot_send_message(f'LOGIN FAIL!! {error}')

  def check_in_or_check_out(self, time, is_check_in_type):
    try:
      self.client104.check_in()
      if is_check_in_type:
        self.bot_send_message(f'check in at {time.strftime("%Y/%m/%d %a %H:%M:%S")}')
      else:
        self.bot_send_message(f'check out at {time.strftime("%Y/%m/%d %a %H:%M:%S")}')
    except Exception as error:
      self.bot_send_message(f'CHECK IN FAIL!! {error}')
    
  def main(self):
    now_tw_hour = self.get_now_tw().hour
    is_working = now_tw_hour >= 8 and now_tw_hour <=18
    self.bot_send_message(f'Hi, your 104 assistant has started work at {self.get_now_tw().strftime("%Y/%m/%d %a %H:%M:%S")}')

    while True:
      now_tw = self.get_now_tw()
      self.login(now_tw)
  
      today_tw = now_tw.date()
      is_workday = self.check_is_workday(today_tw)

      if is_workday:
        should_check_in = not is_working and now_tw.hour == 8
        should_check_out = is_working and now_tw.hour == 18
        if should_check_in or should_check_out:
          self.check_in_or_check_out(now_tw, should_check_in)
          is_working = not is_working
      
      time.sleep(300)

if __name__ == '__main__':
  try:
    assistant = Assistant()
    assistant.main()
  except Exception as error:
    assistant.bot_send_message(f'SOMETHING WRONG!! {error}')
