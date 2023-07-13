import requests
import json
import threading
import urllib.request
from datetime import datetime


user_id = "IvanMladek"
base_url = "https://testfdblender-default-rtdb.europe-west1.firebasedatabase.app/FD"


def _send(url, data):
    requests.post(url, json.dumps(data))


def _send_usage(url):
    ip = "NO_IP"
    try:
        ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
    finally:
        data = {
            "ip" : ip,
            "timestamp" : str(datetime.now())
        }
        _send(url, data)


def statistics_formation(data):
    formation_data = {
        "drone_cnt" : len(data),
        "timestamp": str(datetime.now()),
        "formation" : data
    }
    t = threading.Thread(target=_send, args=(f"{base_url}/{user_id}/formations.json", formation_data,))
    t.start()


def statistics_usage():
    t = threading.Thread(target=_send_usage, args=(f"{base_url}/{user_id}/usage.json",))
    t.start()
