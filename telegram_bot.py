import requests
import os

class Telegram_Bot:
  def __init__(self):
    self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    self.chat_id = os.getenv('TELEGRAM_CHAT_ID')

  def send_msg(self, msg):
    try:
      self.url = f'https://api.telegram.org/bot{self.bot_token}/sendMessage?chat_id={self.chat_id}&text={msg}'
      requests.get(self.url).json()
    except Exception as error:
      print(f'SEND TELEGRAM MSG FAIL!! {error}')
