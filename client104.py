import requests
import os

class Client104:
  def __init__(self):
    self.domain = 'https://pro.104.com.tw'
    self.jwt = ''

  def login(self):
    loginUrl = f'{self.domain}/prohrm/api/login/token'
    acc = os.environ.get('ACC')
    pwd = os.environ.get('PWD')
    loginBody = {
      "uno": "52621439",
      "acc": acc,
      "pwd": pwd,
      "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzb3VyY2UiOiJhcHAtcHJvZCIsImNpZCI6MCwiaWF0IjoxNTUzNzUzMTQwfQ.ieJiJtNsseSO5fxNH1XTa6bqHZ0zUyoPVUYPNtOj4TM"
    }
    response = requests.post(loginUrl, json=loginBody)
    self.jwt = response.json()['data']['access']

  def check_in(self):
    cardUrl = f'{self.domain}/prohrm/api/app/card/gps'
    cardHeaders = {
      "Authorization" : f"Bearer {self.jwt}",
    }
    cardBody = {
      "deviceId": "ADD0E814-AC59-40D4-9073-2AE16FC150E0",
      "latitude": 25.03069017817366,
      "longitude": 121.5574925523737
    }
    requests.post(cardUrl, headers=cardHeaders, json=cardBody)

  def is_OoO_request_form(self, form):
    return form['formCode'] == 101

  def get_in_progress_OoO_form_list(self):
    getInProgressFormUrl = f'{self.domain}/prohrm/api/app/trackForm/inProgress/self'
    getFormHeaders = {
      "Authorization" : f"Bearer {self.jwt}",
    }
    getFormBody = {
      "limit": 10,
      "offset": 0,
    }
    response = requests.post(getInProgressFormUrl, headers=getFormHeaders, json=getFormBody)
    return filter(self.is_OoO_request_form, response.json()['data'])
  
  def get_finished_OoO_form_list(self):
    getFinishedFormUrl = f'{self.domain}/prohrm/api/app/trackForm/finished/self'
    getFormHeaders = {
      "Authorization" : f"Bearer {self.jwt}",
    }
    getFormBody = {
      "limit": 10,
      "offset": 0,
    }
    response = requests.post(getFinishedFormUrl, headers=getFormHeaders, json=getFormBody)
    return filter(self.is_OoO_request_form, response.json()['data'])
