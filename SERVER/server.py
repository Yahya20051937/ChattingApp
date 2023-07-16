import socket
import threading
import logging

PORT = 5050
HEADER = 64
SERVER = socket.gethostbyname(socket.gethostname())
FORMAT = 'utf-8'

ADDR = (SERVER, PORT)

logging.basicConfig(format='%(asctime)s %(levelname)-8s[%(filename)s:%(lineno)d] %(message)s', datefmt='%d-%m-%Y '
                                                                                                       '%H:%M:%S ',
                    level=logging.INFO,
                    filename='server_logs.txt')
logger = logging.getLogger('server')


def handle_client(server, conn, addr):
    from requests import handle_request
    logger.critical(f'New connection from {conn}, {addr}')
    while True:
        request = conn.recv(240).decode(FORMAT)  # get the request and handle it here
        handle_request(server, request, conn)



class Server:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(ADDR)
        self.log_in_users = []   # (conn, id)

    def start(self):
        from database.users_database import create_table

        self.server.listen()
        create_table()

        logger.info('SERVER LISTENING')
        while True:
            conn, addr = self.server.accept()
            thread = threading.Thread(target=handle_client, args=(self, conn, addr))
            thread.start()


if __name__ == '__main__':
    server = Server()
    server.start()
