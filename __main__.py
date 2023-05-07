import atexit
from assistant import Assistant
from dotenv import load_dotenv

def main():
  load_dotenv()
  assistant = Assistant()
  atexit.register(lambda: assistant.bot_send_message('bye~~ (´≖◞౪◟≖)/'))
  assistant.main()

if __name__ == '__main__':
  main()