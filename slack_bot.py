import requests
import os
import json

class Slack_Bot:
  def __init__(self):
    self.slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
    
  def send_msg(self, msg):
    payload = {'text': msg}
    payload_json = json.dumps(payload)
    try:
      requests.post(self.slack_webhook_url, payload_json)
    except Exception as error:
      print(f'SEND SLACK MSG FAIL!! {error}')
