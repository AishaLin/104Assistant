class AbstractProxy:
  def __init__(self):
    self.jwt = ''

  def login(self, user):
    pass

  def check_in_out(self, is_check_in_type, sessionGuid):
    pass

  def check_today_OoO_in_progress_status(self):
    pass

  def check_today_OoO_finished_status(self, today, user_account):
    pass
