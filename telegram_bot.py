from telegram import Bot

class Telegram_Bot:
  def __init__(self):
    bot_token = '6022810965:AAGxuKkqMuJ2OYLlbJa8CtzYCIdPE9XSYAU'
    self.chat_id = 1952480116
    self.bot = Bot(bot_token)

  def send_msg(self, msg):
    self.application.bot.send_message(self.chat_id, msg)
