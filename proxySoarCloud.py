import requests
import xml.etree.ElementTree as ET
from datetime import timedelta, datetime
from telegram_bot import Telegram_Bot
from slack_bot import Slack_Bot
from constants import COMPANY_LAT, COMPANY_LNG, COMPANY_ADDRESS
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

from abstractProxy import AbstractProxy

DOMAIN = 'https://scsservices2.azurewebsites.net'

CHECK_IN__DUTY_CODE = '4'
CHECK_IN__DUTY_STATUS = '4'
CHECK_OUT__DUTY_CODE = '8'
CHECK_OUT__DUTY_STATUS = '5'

SYS__FLOW_FORM_STATUS___COMPLETE = '1'
SYS__FLOW_FORM_STATUS___PENDING = '2'
SYS__FLOW_FORM_STATUS___WITHDRAW = '3'

class ProxySoarCloud(AbstractProxy):
  def __init__(self):
    self.telegram_bot = Telegram_Bot()
    self.slack_bot = Slack_Bot()

  def bot_send_message(self, msg, user_account):
    print(msg)
    self.telegram_bot.send_msg(f'[{user_account}] {msg}')

  def login(self, user_account, user_password):
    url = f'{DOMAIN}/SCSService.asmx'
    headers = {
      "Content-Type": "application/soap+xml",
    }
    payload_xml = """
      <soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
        <soap12:Body>
          <SystemObjectRun xmlns="http://scsservices.net/">
            <args>
              <SessionGuid>00000000-0000-0000-0000-000000000000</SessionGuid>
              <Action>Login</Action>
              <Format>Xml</Format>
              <Bytes/>
              <Value>&lt;?xml version="1.0" encoding="utf-16"?&gt;
                &lt;TLoginInputArgs xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"&gt;
                &lt;AppName&gt;App&lt;/AppName&gt;
                &lt;CompanyID&gt;SCS285&lt;/CompanyID&gt;
                &lt;UserID&gt;__ACC__&lt;/UserID&gt;
                &lt;Password&gt;__PPP__&lt;/Password&gt;
                &lt;LanguageID&gt;zh-TW&lt;/LanguageID&gt;
                &lt;UserHostAddress /&gt;
                &lt;IsSaveSessionBuffer&gt;true&lt;/IsSaveSessionBuffer&gt;
                &lt;ValidateCode /&gt;
                &lt;OAuthType&gt;NotSet&lt;/OAuthType&gt;
                &lt;IsValidateRegister&gt;false&lt;/IsValidateRegister&gt;
                &lt;/TLoginInputArgs&gt;
              </Value>
            </args>
          </SystemObjectRun>
        </soap12:Body>
      </soap12:Envelope>
    """
    payload_xml = payload_xml.replace("__ACC__", str(user_account)).replace("__PPP__", str(user_password))
    response = requests.post(url, data=payload_xml, headers=headers)
    tree = ET.fromstring(response.text)
    namespace = {'ns': 'http://scsservices.net/'}
    value_element = tree.find('.//ns:Value', namespace)
    value_xml = value_element.text
    value_root = ET.fromstring(value_xml)
    result = value_root.find('.//Result').text
    if result == 'false':
      raise Exception('LOGIN FAIL!!')
    else:
      session_guid = value_root.find('.//SessionGuid').text
      return session_guid if session_guid is not None else ''

  def check_in_out(self, is_check_in_type, user_sessionGuid):
    url = f'{DOMAIN}/SCSService.asmx'
    headers = {
      "Content-Type": "application/soap+xml",
    }
    payload_xml = """
      <soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
        <soap12:Body>
          <BusinessObjectRun xmlns="http://scsservices.net/">
            <args>
              <SessionGuid>___SESSION_GUID___</SessionGuid>
              <ProgID>WATT0022000</ProgID>
              <Action>ExecFunc</Action>
              <Format>Xml</Format>
              <Bytes/>
              <Value>&lt;?xml version="1.0" encoding="utf-16"?&gt;
                &lt;TExecFuncInputArgs xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"&gt;
                  &lt;FuncID&gt;ExecuteSwipeData_Web&lt;/FuncID&gt;
                  &lt;Parameters&gt;
                    &lt;Parameter&gt;
                      &lt;Name&gt;DutyCode&lt;/Name&gt;
                      &lt;Value xsi:type="xsd:int"&gt;___DUTY_CODE___&lt;/Value&gt;
                    &lt;/Parameter&gt;
                    &lt;Parameter&gt;
                      &lt;Name&gt;DutyStatus&lt;/Name&gt;
                      &lt;Value xsi:type="xsd:int"&gt;___DUTY_STATUS___&lt;/Value&gt;
                    &lt;/Parameter&gt;
                    &lt;Parameter&gt;
                      &lt;Name&gt;GPSLocation&lt;/Name&gt;
                      &lt;Value xsi:type="xsd:string"&gt;___GPS_LOCATION___&lt;/Value&gt;
                    &lt;/Parameter&gt;
                    &lt;Parameter&gt;
                      &lt;Name&gt;CompanyID&lt;/Name&gt;
                      &lt;Value xsi:type="xsd:string"&gt;SCS285&lt;/Value&gt;
                    &lt;/Parameter&gt;
                    &lt;Parameter&gt;
                      &lt;Name&gt;GpsAddress&lt;/Name&gt;
                      &lt;Value xsi:type="xsd:string"&gt;___GPS_ADDRESS___&lt;/Value&gt;
                    &lt;/Parameter&gt;
                    &lt;Parameter&gt;
                      &lt;Name&gt;NoCheckOnDutyStatus&lt;/Name&gt;
                      &lt;Value xsi:type="xsd:boolean"&gt;true&lt;/Value&gt;
                    &lt;/Parameter&gt;
                  &lt;/Parameters&gt;
                &lt;/TExecFuncInputArgs&gt;
              </Value>
            </args>
          </BusinessObjectRun>
        </soap12:Body>
      </soap12:Envelope>
    """
    dutyCode = CHECK_IN__DUTY_CODE if is_check_in_type else CHECK_OUT__DUTY_CODE
    dutyStatus = CHECK_IN__DUTY_STATUS if is_check_in_type else CHECK_OUT__DUTY_STATUS
    gpsLocation = f'{COMPANY_LAT},{COMPANY_LNG}'
    payload_xml = payload_xml.replace("___SESSION_GUID___", user_sessionGuid).replace("___DUTY_CODE___", dutyCode).replace("___DUTY_STATUS___", dutyStatus).replace("___GPS_LOCATION___", gpsLocation).replace("___GPS_ADDRESS___", COMPANY_ADDRESS)
    response = requests.post(url, data=payload_xml.encode('utf-8'), headers=headers)
    if response.status_code != 200:
      msg = 'CHECK IN FAILED!!' if is_check_in_type else 'CHECK OUT FAILED!!'
      raise Exception(msg)

  # OoO FORM GENERAL HANDLERS
  
  def is_sign_off_completed(self, form, user_account):
    # judge all types as completed except SYS_FLOWFORMSTATUS 3 for now
    form_status_element = form.find(".//SYS_FLOWFORMSTATUS")
    employee_id_element = form.find(".//TMP_EMPLOYEEID")
    if form_status_element is not None:
      return employee_id_element.text == str(user_account) and form_status_element.text != SYS__FLOW_FORM_STATUS___WITHDRAW
    else:
      return False
  
  def parse_summary_text_to_date_list(self, start_date_str, end_date_str):
    start_date = datetime.strptime(start_date_str, "%Y-%m-%dT%H:%M:%S").date()
    end_date = datetime.strptime(end_date_str, "%Y-%m-%dT%H:%M:%S").date()

    date_list = []
    delta = timedelta(days=1)
    current_date = start_date
    while current_date <= end_date:
      date_list.append(current_date)
      current_date += delta
    return date_list
  
  def get_OoO_date_list_from_forms(self, forms):
    OoO_list = set()      
    for watt_element in forms:
      start_date_str = watt_element.findtext("STARTDATE")
      end_date_str = watt_element.findtext("ENDDATE")
      OoO_list_per_form = self.parse_summary_text_to_date_list(start_date_str, end_date_str)
      for OoO_date in OoO_list_per_form:
        OoO_list.add(OoO_date)
    return OoO_list
  
  # IN-PROGRESS FORM HANDLERS

  def check_today_OoO_in_progress_status(self, today):
    # judge all types as completed except SYS_FLOWFORMSTATUS 3 for now
    return False, False
  
  # FINISHED FORM HANDLERS
  
  def get_finished_form_list(self, user_account, user_sessionGuid):
    url = f'{DOMAIN}/SCSService.asmx'
    headers = {
      "Content-Type": "application/soap+xml",
      "Connection": "keep-alive"
    }
    payload_xml = """
      <soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
        <soap12:Body>
          <BOFind xmlns="http://scsservices.net/">
            <inputArgs>
              <SessionGuid>___SESSION_GUID___</SessionGuid>
              <ProgID>WATT0022500</ProgID>
              <Keyword/>
              <SelectFields>*</SelectFields>
              <DateValue>0001-01-01T00:00:00</DateValue>
              <UserFilter>A.DataType = 1</UserFilter>
              <SelectCount>200</SelectCount>
              <SelectSection>0</SelectSection>
              <SourceProgID>WATT0022500</SourceProgID>
              <SourceFieldName/>
            </inputArgs>
          </BOFind>
        </soap12:Body>
      </soap12:Envelope>
    """
    payload_xml = payload_xml.replace("___SESSION_GUID___", user_sessionGuid)

    try:
      response = requests.post(url, data=payload_xml, headers=headers, timeout=5)
    except Exception as error:
      self.bot_send_message(f'GET_FINISHED_FORM_LIST FAILED!! ERROR MSG: {error}', user_account)

    tree = ET.fromstring(response.text)
    watt_elements = tree.findall('.//WATT0022500')
    if response.status_code != 200:
      self.bot_send_message('GET_FINISHED_FORM_LIST FAILED!!', user_account)
    return watt_elements if watt_elements is not None else []
  
  def check_today_OoO_finished_status(self, today, user_account, user_sessionGuid):
    finishedOoORequestForms = list(filter(lambda form: self.is_sign_off_completed(form, user_account), self.get_finished_form_list(user_account, user_sessionGuid)))
    finishedOoORequestDateList = self.get_OoO_date_list_from_forms(finishedOoORequestForms)
    return today in finishedOoORequestDateList, False
