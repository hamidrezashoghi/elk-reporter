#!/usr/bin/env python3

import os
import threading
from dotenv import load_dotenv
from web_server import WebServer


def main():
    # ENV variables
    load_dotenv()
    es_host = os.getenv('ES_HOST')
    es_port = os.getenv('ES_PORT')
    es_username = os.getenv('ES_USERNAME')
    es_password = os.getenv('ES_PASSWORD')

    web_server_ip = os.getenv('WEB_SERVER_IP')
    web_server_port = os.getenv('WEB_SERVER_PORT')

    web_server = WebServer(web_server_ip, web_server_port, es_host, es_port, es_username, es_password)
    threading.Thread(target=web_server.run).start()


if __name__ == '__main__':
    main()
