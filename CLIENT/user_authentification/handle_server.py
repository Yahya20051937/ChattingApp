import json
import pickle
import socket
from types import coroutine
from threading import Thread


@coroutine
def send_user_auth_request(client, val):
    from client import logger
    from objects import User
    from user_authentification.templates import sign_up_page, log_in_page
    from chatting.handle_server import send_request_co, send_request

    from chatting.templates import home_page

    PORT = 5050
    HEADER = 64
    FORMAT = 'utf-8'

    while True:
        func, data_json = yield

        request = f'/{val}/{data_json}'  # create the request, either and sign up or log in, along with the data the user provided

        client.sendall(request.encode(FORMAT))  # send the data to the server
        statement = client.recv(HEADER).decode(FORMAT)

        logger.info(f'statement: {statement}')
        # if the statement is true, then we move the user to the home page, otherwise, we either move it to sign up or log in page

        if statement == 'True':
            user_data = client.recv(1000)
            user_data_list = pickle.loads(user_data)

            # we create a user object and coroutine that will be used later to send request to the server, and pass them to the homepage function

            send_request_function = send_request(send_request_co(
                client))  # create two function , one to send messages to the user with whom we started the conversation, and another when to receive messages from this user
            send_request_function.send(None)

            user = User(id=user_data_list[0], username=user_data_list[1], connection=client,
                        send_request_func=send_request_function)
            user.status = 'online'
            send_request_function.send(f'/is_online/{user.id}')
            home_page(user=user, auth_func=func)

        else:

            if val == 'sign_up':
                sign_up_page(func, statement=statement)
            elif val == 'log_in':

                log_in_page(func, statement=statement)


async def user_auth_request(g):
    await g
