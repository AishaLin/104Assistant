import requests
import json

class Slack_Bot:    
  def send_msg(self, slack_webhook_url, msg):
    payload = {'text': msg}
    payload_json = json.dumps(payload)
    try:
      requests.post(slack_webhook_url, payload_json)
    except Exception as error:
      print(f'SEND SLACK MSG FAIL!! {error}')
