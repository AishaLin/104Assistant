## 功能 ##
* 提供兩種打卡平台
  * 104 企業大師(未持續維護)
  * 飛騰雲端(default)
* 打卡條件：
  * 只在上班日打卡；即週末、國定假日、簽核中/簽核完成之休假日，不打卡
  * 上述之休假日只抓日期；即全天休假/休假時數不滿一日，皆不打卡
  * 若有銷假/抽單：
    * 假單已抽單，會打卡
    * 假單簽核完成後申請銷假單，不管銷假單狀態是簽核中/簽核完成，皆會打卡

## 須建立 config.py，可執行多組帳號 ##

* config.py 範例
  ```
  APP='104'/'SoarCloud'
  TELEGRAM_BOT_TOKEN = 'xxxxxxxxx'
  TELEGRAM_CHAT_ID = 1234567

  user_list = [
    {
      'ACC': 'account',
      'PPP': 'password',
      'NAME': 'Aisha',
    },
  ]
  ```

* if you want to receive alert/warning from slack (optional)
  * you can get SLACK_WEBHOOK_URL from [Slack API documentation](https://taxigo-tw.slack.com/apps/new/A0F7XDUAZ-incoming-webhooks)
  ```
  SLACK_WEBHOOK_URL='https://hooks.slack.com/services/XXX/XXX/XXX'
  ```

## GOGO！ ##
```
python3 __main__.py
```