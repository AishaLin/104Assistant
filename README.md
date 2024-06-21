### 功能 ###

* 提供兩種打卡平台
  * 104 企業大師(未持續維護)
  * 飛騰雲端(default)

* 只在上班日打卡：
  * 週末、國定假日、簽核中/簽核完成之休假日，不打卡
  * 上述之休假日只抓日期；即全天休假/休假時數不滿一日，皆不打卡
  * 若有銷假/抽單：
    * 假單已抽單，會打卡
    * 假單簽核完成後申請銷假單，不管銷假單狀態是簽核中/簽核完成，皆會打卡


### 步驟 ###

  * 開一台機器 (Oracle 可以開免費機器，但不太穩定)
  * git clone
  * 安裝 python
      ```
      sudo apt update
      sudo apt install python3-pip
      ```
  * 安裝 requirements 內 packages
      ```
      pip3 install -r requirements.txt
      ```
  * 須建立 config.py，可執行多組帳號
    * 指令
        ```
        vim config.py
        ```
    * 範例：
        ```
        APP='104'/'SoarCloud'
        TELEGRAM_BOT_TOKEN = 'xxxxxxxxx'
        TELEGRAM_CHAT_ID = 1234567

        user_list = [
          {
            'ACC': 'account',
            'PPP': 'password',
            'NAME': 'Aisha',
            'SLACK_WEBHOOK_URL': None,
          },
        ]
        ```
  * 設置排程(CronJob)
    * 安裝
        ```
        sudo apt update
        sudo apt install cron
        ```
    * 確認時區
        ```
        timedatectl
        ```
    * 修改時區
        ```
        sudo timedatectl set-timezone Asia/Taipei
        ```
    * 編輯 crontab 內容，設置排程
        ```
        # 進入編輯
        crontab -e

        # 排程範例
        # 為了實現自然的打卡時間且避免太過頻繁發 request，user 間有 random sleep，起迄時間建議 8hr 再 + 10 分鐘 buffer
        57 9 * * 1-5 /usr/bin/python3 /home/ubuntu/104Assistant/__main__.py >> /home/ubuntu/104Assistant/cron_output.log 2>&1
        07 19 * * 1-5 /usr/bin/python3 /home/ubuntu/104Assistant/__main__.py >> /home/ubuntu/104Assistant/cron_output.log 2>&1
        ```
    * 查看自己的 crontab
        ```
        crontab -l
        ```
    * 啟動並運行 cron
        ```
        sudo systemctl start cron
        sudo systemctl enable cron
        ```
    * 檢查 cron 狀態，是否有在運行
        ```
        sudo systemctl status cron
        ```


### 其他 ###

* if you want to receive alert/warning from slack (optional)
  * you can get SLACK_WEBHOOK_URL from [Slack API documentation](https://taxigo-tw.slack.com/apps/new/A0F7XDUAZ-incoming-webhooks)
  ```
  SLACK_WEBHOOK_URL='https://hooks.slack.com/services/XXX/XXX/XXX'
  ```
