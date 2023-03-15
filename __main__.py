from assistant import Assistant
from dotenv import load_dotenv

def main():
  load_dotenv()
  assistant = Assistant()
  assistant.main()

if __name__ == '__main__':
  main()