import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

class Telegram_Bot:
  def send_msg(self, msg):
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
      try:
        self.url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={msg}'
        requests.get(self.url).json()
      except Exception as error:
        print(f'SEND TELEGRAM MSG FAIL!! {error}')
