import requests
from datetime import date, timedelta
from constants import COMPANY_LAT, COMPANY_LNG

from abstractProxy import AbstractProxy

DOMAIN = 'https://pro.104.com.tw'

FORM_CODE__OOO_REQUEST = 101
FORM_CODE__OOO_WITHDRAW = 107

REQUEST_STATUS__IN_PROGRESS = 1
REQUEST_STATUS__COMPLETED = 2
REQUEST_STATUS__WITHDRAW = 4

class Proxy104(AbstractProxy):
  def __init__(self):
    self.jwt = ''

  def login(self, user):
    url = f'{DOMAIN}/prohrm/api/login/token'
    body = {
      "uno": "52621439",
      "acc": user.account,
      "pwd": user.password,
      "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzb3VyY2UiOiJhcHAtcHJvZCIsImNpZCI6MCwiaWF0IjoxNTUzNzUzMTQwfQ.ieJiJtNsseSO5fxNH1XTa6bqHZ0zUyoPVUYPNtOj4TM"
    }
    response = requests.post(url, json=body)
    self.jwt = response.json()['data']['access']

  def check_in_out(self, is_check_in_type):
    url = f'{DOMAIN}/prohrm/api/app/card/gps'
    headers = {
      "Authorization" : f"Bearer {self.jwt}",
    }
    body = {
      "deviceId": "ADD0E814-AC59-40D4-9073-2AE16FC150E0",
      "latitude": COMPANY_LAT,
      "longitude": COMPANY_LNG
    }
    requests.post(url, headers=headers, json=body)

  # OoO FORM GENERAL HANDLERS

  def is_OoO_request_type(self, form):
    return form['formCode'] == FORM_CODE__OOO_REQUEST
  
  def is_OoO_withdraw_type(self, form):
    return form['formCode'] == FORM_CODE__OOO_WITHDRAW
  
  def is_sign_off_completed(self, form):
    return form['requestStatus'] == REQUEST_STATUS__COMPLETED
  
  def convert_date_str_to_datetime(self, date_str):
    date_parts = date_str.split('/')
    if len(date_parts) < 3:
      return None
    year = int(date_parts[0])
    month = int(date_parts[1])
    day = int(date_parts[2])
    return date(year, month, day)
  
  def parse_summary_text_to_date_list(self, summary_text):
    start_date_str = summary_text.split(' ')[0]
    start_date = self.convert_date_str_to_datetime(start_date_str)
    end_date_str = summary_text.split('~ ')[1].split(' ')[0] if len(summary_text.split('~ ')) > 1 and len(summary_text.split('~ ')[1].split(' ')) > 0 else start_date_str
    end_date = self.convert_date_str_to_datetime(end_date_str) or start_date

    date_list = []
    delta = timedelta(days=1)
    current_date = start_date
    while current_date <= end_date:
      date_list.append(current_date)
      current_date += delta
    return date_list
  
  def get_OoO_date_list_from_forms(self, forms):
    OoO_list = set()
    for item in forms:
      summary_text = item['summary']
      OoO_list_per_form = self.parse_summary_text_to_date_list(summary_text)
      for OoO_date in OoO_list_per_form:
        OoO_list.add(OoO_date)
    return OoO_list
  
  # IN-PROGRESS FORM HANDLERS

  def get_in_progress_form_list(self):
    url = f'{DOMAIN}/prohrm/api/app/trackForm/inProgress/self'
    headers = {
      "Authorization" : f"Bearer {self.jwt}",
    }
    body = {
      "limit": 10,
      "offset": 0,
    }
    response = requests.post(url, headers=headers, json=body)
    return response.json()['data']

  def check_today_OoO_in_progress_status(self, today):
    inProgressForms = self.get_in_progress_form_list()
    inProgressOoORequestForms = filter(self.is_OoO_request_type, inProgressForms)
    inProgressOoOWithdrawForms = filter(self.is_OoO_withdraw_type, inProgressForms)
    inProgressOoORequestDateList = self.get_OoO_date_list_from_forms(inProgressOoORequestForms)
    inProgressOoOWithdrawDateList = self.get_OoO_date_list_from_forms(inProgressOoOWithdrawForms)
    return today in inProgressOoORequestDateList, today in inProgressOoOWithdrawDateList
  
  # FINISHED FORM HANDLERS
  
  def get_finished_form_list(self):
    url = f'{DOMAIN}/prohrm/api/app/trackForm/finished/self'
    headers = {
      "Authorization" : f"Bearer {self.jwt}",
    }
    body = {
      "limit": 10,
      "offset": 0,
    }
    response = requests.post(url, headers=headers, json=body)
    return response.json()['data']
  
  def check_today_OoO_finished_status(self, today):
    finishedForms = list(filter(self.is_sign_off_completed, self.get_finished_form_list()))
    finishedOoORequestForms = filter(self.is_OoO_request_type, finishedForms)
    finishedOoOWithdrawForms = filter(self.is_OoO_withdraw_type, finishedForms)
    finishedOoORequestDateList = self.get_OoO_date_list_from_forms(finishedOoORequestForms)
    finishedOoOWithdrawDateList = self.get_OoO_date_list_from_forms(finishedOoOWithdrawForms)
    return today in finishedOoORequestDateList, today in finishedOoOWithdrawDateList
