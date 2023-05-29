## 功能 ##
* 只在上班日打卡；即週末、國定假日、簽核中/簽核完成之休假日 --> 不打卡
* 休假日只抓日期，全天休假/休假時數不滿一日 --> 皆不打卡
* 若假單已抽單 --> 打卡
* 若假單簽核完成後申請銷假單；不管銷假單狀態是簽核中/簽核完成 --> 打卡

## 須設置環境變數 ##

* required items for login your account
```
APP='104' or 'SoarCloud' (default = 'SoarCloud')
ACC='account'
PPP='password'
```

* if you want to receive alert/warning from telegram (optional)
```
TELEGRAM_BOT_TOKEN=''
TELEGRAM_CHAT_ID=number
```

* if you want to receive alert/warning from slack (optional)
  * you can get SLACK_WEBHOOK_URL from [Slack API documentation](https://taxigo-tw.slack.com/apps/new/A0F7XDUAZ-incoming-webhooks)
```
SLACK_WEBHOOK_URL='https://hooks.slack.com/services/XXXXXXXXX/XXXXXXXXXXX/XXXXXXXXXXXXXXXXXXXXXXXX'
```
