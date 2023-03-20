from datetime import date

DOMAIN = 'https://pro.104.com.tw'

FORM_CODE__OOO_REQUEST = 101
FORM_CODE__OOO_WITHDRAW = 107

REQUEST_STATUS__IN_PROGRESS = 1
REQUEST_STATUS__COMPLETED = 2
REQUEST_STATUS__WITHDRAW = 4

NATIONAL_HOLIDAYS = set([
  date(2023, 2, 27),
  date(2023, 2, 28),
  date(2023, 4, 3),
  date(2023, 4, 4),
  date(2023, 4, 5),
  date(2023, 5, 1),
  date(2023, 6, 22),
  date(2023, 6, 23),
  date(2023, 9, 29),
  date(2023, 10, 9),
  date(2023, 10, 10),
  date(2024, 1, 1),
])