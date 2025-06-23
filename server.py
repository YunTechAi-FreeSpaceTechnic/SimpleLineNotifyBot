import os

from flask import Flask, request, abort

from datetime import datetime
from pyngrok import ngrok, conf
from pyngrok.conf import PyngrokConfig
from typing import List
import pyngrok.conf

from linebot.v3 import (
    WebhookHandler,
    WebhookParser
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    MulticastRequest,
    TextMessage,
    PushMessageRequest,
)

from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    ImageMessageContent,
    VideoMessageContent,
    AudioMessageContent,
    FileMessageContent,
    StickerMessageContent,
    LocationMessageContent
)


class LineBotFlaskServer:
    def __init__(self, line_access_token: str, line_channel_secret: str, ngrok_token: str, ngrok_domain: str, port: int, multicast_users: List[str]):
        self.ngrok_token = ngrok_token
        self.ngrok_domain = ngrok_domain
        self.port = port
        self.multicast_users = multicast_users

        self.line_config = Configuration(access_token=line_access_token)
        self.handler = WebhookHandler(channel_secret=line_channel_secret)

        self.app = Flask(__name__)
        self._build_routes()
        
        os.makedirs('history', exist_ok=True)
    
    def get_message_str(event_message):
        if isinstance(event_message, TextMessageContent):
            return event_message.text
        if isinstance(event_message, ImageMessageContent):
            return '[圖片]'
        if isinstance(event_message, VideoMessageContent):
            return f'[影片 長度{event_message.duration/1000:.0f}秒]'
        if isinstance(event_message, AudioMessageContent):
            return f'[音訊 長度{event_message.duration/1000:.0f}秒]'
        if isinstance(event_message, FileMessageContent):
            return f'[檔案 "{event_message.fileName}"]'
        if isinstance(event_message, StickerMessageContent):
            return '[貼圖]'
        if isinstance(event_message, LocationMessageContent):
            return f'[位置 {event_message.address}]'
        return '[未知訊息]'
    
    def _build_routes(self):
        @self.app.route("/callback", methods=['POST'])
        def callback():
            signature = request.headers['X-Line-Signature']
            body = request.get_data(as_text=True)
            try:
                self.handler.handle(body, signature)
            except InvalidSignatureError:
                self.app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
                abort(400)
            return 'OK'

        @self.handler.add(MessageEvent)
        def handle_message(event):
            with ApiClient(self.line_config) as api_client:
                line_bot_api = MessagingApi(api_client)
                
                user_profile = line_bot_api.get_profile(event.source.user_id)
                time = datetime.now()                
                user_message_str = LineBotFlaskServer.get_message_str(event.message)

                channel_id = event.source.user_id
                if event.source.type == 'group':
                    channel_id = event.source.group_id
                elif event.source.type == 'room':
                    channel_id = event.source.room_id

                self.app.logger.info(f'{channel_id}:"{user_profile.display_name}":"{user_message_str}"')

                # save to file
                with open(f'history/{time.strftime("%Y-%m-%d")}.txt', 'a', encoding='utf-8') as f:
                    f.write(f'{time.strftime("%H:%M:%S.%f")},"{event.source.user_id}","{user_profile.display_name}","{user_message_str}"\n')
                    f.flush()

                # send to multicast_users
                for to_id in self.multicast_users:
                    if to_id == channel_id:
                        continue
                    line_bot_api.push_message(
                        PushMessageRequest(
                            to=to_id,
                            messages=[TextMessage(text=f'{user_profile.display_name}：\n{user_message_str}')]
                        )
                    )

    def run(self):
        ngrok_config = PyngrokConfig()
        ngrok_config.ngrok_path = 'ngrok.exe'
        ngrok_config.auth_token = self.ngrok_token
        ngrok.connect(addr=self.port, domain=self.ngrok_domain, pyngrok_config=ngrok_config)

        self.app.run(host='0.0.0.0', port=self.port)

# pyngrok console window fix
# pyngrok/process.py line:408
# - popen_kwargs: Dict[str, Any] = {"stdout": subprocess.PIPE, "universal_newlines": True}
# + popen_kwargs: Dict[str, Any] = {"stdout": subprocess.PIPE, "universal_newlines": True, "creationflags": subprocess.CREATE_NO_WINDOW}
