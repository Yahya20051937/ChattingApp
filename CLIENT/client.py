import tkinter as tk
import logging
import socket
from user_authentification.templates import user_auth_home_page
from user_authentification.handle_server import user_auth_request, send_user_auth_request

from collections import deque

logging.basicConfig(format='%(asctime)s %(levelname)-8s[%(filename)s:%(lineno)d] %(message)s', datefmt='%d-%m-%Y '
                                                                                                       '%H:%M:%S ',
                    level=logging.INFO,
                    filename='client_logs.txt')
logger = logging.getLogger('client')


def connect():
    PORT = 5050
    HEADER = 64
    SERVER = socket.gethostbyname(socket.gethostname())
    FORMAT = 'utf-8'

    ADDR = (SERVER, PORT)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)

    func1 = user_auth_request(send_user_auth_request(client, 'sign_up'))
    func2 = user_auth_request(send_user_auth_request(client, 'log_in'))

    func1.send(None)
    func2.send(None)

    user_auth_home_page(func1, func2)


if __name__ == '__main__':
    connect()
    tk.mainloop()
