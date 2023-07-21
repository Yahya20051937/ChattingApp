import json
import pickle


def handle_sign_up_request(request, conn, server):
    from user_authentification.authentification import sign_up_auth
    from server import logger
    from database.users_database import add_user, get_user

    request_dict = json.loads(request)

    username = request_dict['username']
    email = request_dict['email']
    password = request_dict['password']
    confirm_password = request_dict['confirm_password']

    logger.info(
        f'sing up request : username : {username}, password : {password} email : {email}, confirm password: {confirm_password}')

    validation, error_or_id = sign_up_auth(username=username, email=email, password=password,
                                           check_password=confirm_password)  # if the auth is valid, then the second variable will hold the id, otherwise, the second variable will hold the error

    if validation:
        add_user(userid=error_or_id, username=username, email=email,
                 password=password)  # if the authentication is valid, we add the user to the users_database

    sign_up_response(server, conn, validation, error_or_id)


def sign_up_response(server, conn, validation, error_or_id):
    from SERVER.database.users_database import get_user, get_users_data
    from SERVER.database.chatting_databases import create_request_table

    if validation:
        server.log_in_users.append((conn,
                                    error_or_id))  # if the user is logged in, we add the connection and the id to the login users attribute of the server
        user_data = get_user(
            error_or_id)  # we get the userdata from the database using the id, and then we send in back to the client if the authentication is valid
        conn.sendall('True'.encode('utf-8'))
        user_data_as_pickle = pickle.dumps(user_data)

        # user just signed up, so he has no friends, so we will send empty data just to avoid crashing the program
        create_request_table(user_data[0])
        conn.sendall(user_data_as_pickle)
        send_friends_data(conn, [])
        send_all_conversations(conn, user_data)
        send_all_requests(conn, user_data[0])

    else:
        conn.sendall(error_or_id.encode('utf-8'))  # or we just send the error


def handle_log_in_request(request, conn, server):
    from server import logger
    from user_authentification.authentification import log_in_auth

    request_dict = json.loads(request)

    username = request_dict['username']
    password = request_dict['password']

    logger.info(f'log in request : username : {username}, password : {password}')

    validation, statement = log_in_auth(username=username, password=password)
    log_in_response(server, conn, validation, statement, username)


def log_in_response(server, conn, validation, statement, username):
    from SERVER.database.users_database import get_user, get_users_data, get_user_friends, \
        create_conversation_data_table
    from SERVER.database.chatting_databases import create_request_table

    if validation:

        user_data = get_user(username,
                             'username')  # we get the userdata user the username, and we send it to the client.
        server.log_in_users.append((conn, user_data[
            0]))  # if the user is logged in, we add the connection and the id to the login users attribute of the server

        conn.sendall('True'.encode('utf-8'))
        user_data_as_pickle = pickle.dumps(user_data)
        create_request_table(user_data[0])
        friends = get_user_friends(user_data[0])

        conn.sendall(user_data_as_pickle)
        send_friends_data(server, conn, friends)
        send_all_conversations(conn, user_data)
        send_all_requests(conn, user_data[0])

    else:
        conn.sendall(statement.encode('utf-8'))


def send_all_conversations(conn, user_data):
    from SERVER.database.users_database import get_all_conversations_info
    from SERVER.database.chatting_databases import get_conversation
    user_id = user_data[0]
    user_conversations = []
    all_conversations_info = get_all_conversations_info()
    # print(all_conversations_info)
    for conversation in all_conversations_info:
        members = conversation[1].split('-')

        if int(user_id) in [int(member_id) for member_id in members]:
            conv_id = conversation[0]
            conv_name = conversation[2]
            content = get_conversation(conv_id=conv_id)
            user_conversations.append((conv_id, conv_name, members, content))  # int , str, list, list
    # print(user_conversations)
    user_conversations_pickle = pickle.dumps(user_conversations)
    conn.sendall(user_conversations_pickle)


def send_friends_data(server, conn, friends_data):
    i = - 1
    for data in friends_data:
        i += 1
        data = list(data)
        if int(data[0]) in [int(user[1]) for user in server.log_in_users]:
            data.append('online')
        else:
            data.append('offline')
        friends_data[i] = data

    friends_data_pickle = pickle.dumps(friends_data)

    conn.sendall(friends_data_pickle)


def send_all_requests(conn, user_id):
    from database.chatting_databases import get_all_requests
    all_requests = get_all_requests(user_id)

    all_requests_as_pickle = pickle.dumps(all_requests)
    conn.sendall(all_requests_as_pickle)
