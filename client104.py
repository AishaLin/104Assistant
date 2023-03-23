import requests
import os
from constants import DOMAIN

class Client104:
  def __init__(self):
    self.jwt = ''

  def login(self):
    loginUrl = f'{DOMAIN}/prohrm/api/login/token'
    acc = os.getenv('ACC')
    pwd = os.getenv('PPP')
    loginBody = {
      "uno": "52621439",
      "acc": acc,
      "pwd": pwd,
      "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzb3VyY2UiOiJhcHAtcHJvZCIsImNpZCI6MCwiaWF0IjoxNTUzNzUzMTQwfQ.ieJiJtNsseSO5fxNH1XTa6bqHZ0zUyoPVUYPNtOj4TM"
    }
    response = requests.post(loginUrl, json=loginBody)
    self.jwt = response.json()['data']['access']

  def check_in(self):
    cardUrl = f'{DOMAIN}/prohrm/api/app/card/gps'
    cardHeaders = {
      "Authorization" : f"Bearer {self.jwt}",
    }
    cardBody = {
      "deviceId": "ADD0E814-AC59-40D4-9073-2AE16FC150E0",
      "latitude": 25.039281,
      "longitude": 121.5480778
    }
    requests.post(cardUrl, headers=cardHeaders, json=cardBody)

  def get_in_progress_form_list(self):
    getInProgressFormUrl = f'{DOMAIN}/prohrm/api/app/trackForm/inProgress/self'
    getFormHeaders = {
      "Authorization" : f"Bearer {self.jwt}",
    }
    getFormBody = {
      "limit": 10,
      "offset": 0,
    }
    response = requests.post(getInProgressFormUrl, headers=getFormHeaders, json=getFormBody)
    return response.json()['data']
  
  def get_finished_form_list(self):
    getFinishedFormUrl = f'{DOMAIN}/prohrm/api/app/trackForm/finished/self'
    getFormHeaders = {
      "Authorization" : f"Bearer {self.jwt}",
    }
    getFormBody = {
      "limit": 10,
      "offset": 0,
    }
    response = requests.post(getFinishedFormUrl, headers=getFormHeaders, json=getFormBody)
    return response.json()['data']
