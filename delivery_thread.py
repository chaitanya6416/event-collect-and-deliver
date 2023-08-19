# delivery_thread.py
import threading
import requests
import json
from logger import logger
from tenacity import retry, stop_after_attempt, wait_fixed
from redis_client import redis_client


class DeliveryThread(threading.Thread):
    def __init__(self, port):
        super().__init__()
        self.port = port
        self.delivered_key = f"port_{port}_delivered"
        self.running = True