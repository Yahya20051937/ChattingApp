import json
import time
import threading
from types import coroutine
import pickle
from threading import Thread

stop_flag = threading.Event()


@coroutine
def send_request_co(client):
    FORMAT = 'utf-8'
    while True:

        request = yield
        print(request)
        client.sendall(request.encode(FORMAT))


async def send_request(g):
    await g
