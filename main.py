import sys
import threading
from PyQt5.QtWidgets import QApplication
import logging
import yaml

from server import LineBotFlaskServer
from app import LogViewerApp


def main():
    with open('config.yml', 'r', encoding='utf-8') as f:
        root_config = yaml.safe_load(f)

    app_config = root_config.get('log', {})
    viewer_app = LogViewerApp(
        app=QApplication(sys.argv),
        log_maxlen=app_config.get('maxlen', 1000),
        log_format=app_config.get('format', '%(asctime)s - %(message)s'),
        log_level=app_config.get('level', logging.INFO),
        show_at_run=app_config.get('show_at_run', True),
    )

    server_config = root_config.get('server', {})
    server = LineBotFlaskServer(
        line_access_token=server_config.get('line_access_token', ''),
        line_channel_secret=server_config.get('line_channel_secret', ''),
        ngrok_token=server_config.get('ngrok_token', ''),
        ngrok_domain=server_config.get('ngrok_domain', ''),
        port=server_config.get('port', 50033),
        multicast_users=root_config.get('multicast_users', []),
    )

    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()
    viewer_app.run()


if __name__ == '__main__':
    main()
