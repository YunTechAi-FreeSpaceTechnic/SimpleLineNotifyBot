# SimpleLineNotifyBot
簡單的Line訊息轉發機器人

---
### 快速設定指南 (Windows)
##### 一、下載必要檔案
1. 從 [Release 頁面](https://github.com/YunTechAi-FreeSpaceTechnic/SimpleLineNotifyBot/releases) 下載並解壓縮。
2. 下載 ngrok https://ngrok.com/downloads/windows?tab=download
    解壓後將 `ngrok.exe` 放入與 `main.exe` 同一資料夾。
3. 開啟 `config.yml`，依以下說明完成設定。

##### 二、設定 Ngrok
1. 前往 https://dashboard.ngrok.com/signup 建立帳號
2. 在 **Getting Started / Your Authtoken** 頁面：
   - 複製 Authtoken
   - 貼上到 `config.yml` 中的 `NGROK_TOKEN` 欄位
3. 在 **Universal Gateway / Domains** 頁面：
   - 點擊 `+ New Domain` 建立新網域
   - 複製新建立的網址到 `config.yml` 中的 `NGROK_DOMAIN` 欄位

##### 三、設定 Line
1. 前往 https://developers.line.biz/console/ 並登入您的帳號
2. 建立新的 Messaging API Channel 或選擇現有的
3. 在 **Basic Settings** 頁面：
   - 找到 `Channel Secret`
   - 複製到 `config.yml` 中的 `LINE_CHANNEL_SECRET`
4. 在 **Messaging API** 頁面：
   - 找到 `Channel Access Token`
   - 複製到 `config.yml` 中的 `LINE_ACCESS_TOKEN`
   - 找到 `Webhook URL` 設定
   - 設定為：`https://你的ngrok網域/callback`
   - 啟用 `Use webhook`

##### 四、將 `config.yml`  內的`multicast_users` 改成要接收通知的使用者或調天室ID
```yml
multicast_users:
- "C9f8c7d7a6468392438a242e3f5f0abcd" #像這樣
```

##### 五、最後 `config.yml` 應該會像這樣
```yml
log:
    maxlen: 1000
    format: "[%(asctime)s] %(message)s"
    level: INFO
    show_at_run: true

server:
    line_access_token: "aiPt0FJIIXR02yuyh..."
    line_channel_secret: "164697be9a60eea..."
    ngrok_token: "2wfnjZH4HinwIV4EiejPQSt..."
    ngrok_domain: "abcd.ngrok-free.app"
    port: 50033

multicast_users:
    - "C9f8c7d7a6468392438a242e3f5f0abcd"
```

##### 六、設置完畢 儲存 `config.yml` 並開啟 `main.exe`

---
### 他是如何運作的
程式分為 `app.py` 和 `server.py` 兩個部分
- app.py
    會向 logging 註冊一個 Handler 來擷取所有日誌，並顯示在UI上
- server.py
    使用 Flask 建立簡單的Http伺服器，用於接收來自Line的Webhook
    再將接收到的訊息透過line bot api傳送至指定的聊天室
---
### 建置
- 安裝套件 
    ```
    pip install -r requirements.txt
    ```
- 建置
使用 `build.bat` 或是
    ```
    pyinstaller --onefile --windowed main.py
    ```
