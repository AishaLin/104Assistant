class User:
  def __init__(self, account, password, name, is_workday, user_sessionGuid, slack_webhook_url = None):
    self.account = account
    self.password = password
    self.name = name
    self.slack_webhook_url = slack_webhook_url

    # init state
    self.is_workday = is_workday
    self.sessionGuid = user_sessionGuid
        