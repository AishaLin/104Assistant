import requests

class Telegram_Bot:
  def __init__(self):
    self.bot_token = '6022810965:AAGxuKkqMuJ2OYLlbJa8CtzYCIdPE9XSYAU'
    self.chat_id = 1952480116

  def send_msg(self, msg):
    self.url = f'https://api.telegram.org/bot{self.bot_token}/sendMessage?chat_id={self.chat_id}&text={msg}'
    requests.get(self.url).json()
