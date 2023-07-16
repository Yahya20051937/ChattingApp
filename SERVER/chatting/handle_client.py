import pickle
import json


def handle_send_text_request(server, conn, user_id, conv_id, friend_id, msg_id, message):
    from chatting.function import find_logged_in_user
    from database.chatting_databases import add_message

    bool_value, friend_connection = find_logged_in_user(server, int(friend_id))

    if bool_value:  # the friend is logged in, so we send him the message directly
        message_dict = {'sender': user_id, 'message': message}
        message_json = json.dumps(message_dict)
        response = f'message/{message_json}'
        friend_connection.sendall(response.encode('utf-8'))
        distributed_response = f'message_is_distributed/{friend_id}/{msg_id}'  # this will be a response to inform the client side that message has been distributed
        conn.sendall(distributed_response.encode('utf-8'))
    add_message(table_owner_id=user_id, sender_id=user_id, receiver_id=friend_id, friend_id=friend_id, message=message)
    add_message(table_owner_id=friend_id, sender_id=user_id, receiver_id=friend_id, friend_id=user_id,
                message=message)


def handle_grp_send_text_request(server, conn, user_id, conv_id, friends_ids, msg_id, message):
    from chatting.function import find_logged_in_user
    from database.chatting_databases import add_grp_message, add_message

    friends_ids = friends_ids.split('-')
    for friend_id in friends_ids:
        bool_value, friend_connection = find_logged_in_user(server, int(friend_id))

        if bool_value:
            message_dict = {'sender': user_id, 'message': message}
            message_json = json.dumps(message_dict)
            response = f'grp_message/{conv_id}/{message_json}'
            friend_connection.sendall(response.encode('utf-8'))
        add_grp_message(table_owner_id=friend_id, conv_id=conv_id, sender_id=user_id, message=message)
    add_grp_message(table_owner_id=user_id, conv_id=conv_id, sender_id=user_id, message=message)


def handle_add_friend_request(server, conn, user_id, friend_username):
    from chatting.function import find_logged_in_user
    from database.users_database import get_users_data, get_user
    from database.chatting_databases import add_request

    usernames = [user[1] for user in get_users_data()]
    if friend_username in usernames:
        friend_id = get_user(friend_username, by='username')[0]
        username = get_user(user_id, by='id')[1]
        bool_value, friend_connection = find_logged_in_user(server, int(friend_id))
        if bool_value:  # if the user is logged in we send him the request directly, and we add the request to the database, otherwise we just add it to the database, so he can see it later
            username = get_user(user_id)[1]  # we get the user from the database
            request = f'friend_request/{username}/{user_id}'
            friend_connection.sendall(request.encode('utf-8'))

        add_request(requested_user_id=friend_id, requesting_user_id=user_id,
                    requesting_user_username=username)  # add the request to the database and send the response back to the client
        conn.sendall('friend_response/Request sent'.encode('utf-8'))
    else:
        conn.sendall('friend_response/username not found'.encode('utf-8'))


def handle_accept_request(server, conn, user_id, friend_id):
    from database.users_database import add_friend, get_user, get_user_friends
    from database.chatting_databases import delete_request, create_table
    from chatting.function import find_logged_in_user

    if int(friend_id) not in [int(f[0]) for f in get_user_friends(user_id)] and user_id not in [int(f[0]) for f in
                                                                                                get_user_friends(
                                                                                                    friend_id)]:  # if one of the user has already accepted a request and both of them have sent in to each other we should do this process only once

        add_friend(user_id, friend_id)
        add_friend(friend_id, user_id)
        delete_request(user_id, friend_id)
        create_table(user_id, friend_id)
        create_table(friend_id, user_id)
        username = get_user(user_id, by='id')[1]
        bool_value, friend_connection = find_logged_in_user(server, int(friend_id))
        if bool_value:
            response = f'friend_request_accepted/{user_id}/{username}'
            friend_connection.sendall(response.encode('utf-8'))


def handle_decline_request(server, conn, user_id, friend_id):
    from database.chatting_databases import delete_request
    delete_request(user_id, friend_id)


def handle_message_is_seen_request(server, conn, user_id, friend_id, msg_id):
    from chatting.function import find_logged_in_user
    from database.chatting_databases import edit_message_to_seen

    bool_value, friend_connection = find_logged_in_user(server, int(friend_id))
    if bool_value:  # if the user is logged in, we send him directly the response, that his message is seen by the user.
        response = f'message_is_seen/{user_id}/{msg_id}'
        friend_connection.sendall(response.encode('utf-8'))

    edit_message_to_seen(table_owner_id=user_id, friend_id=friend_id, msg_id=msg_id)  # and we edit both tables.
    edit_message_to_seen(table_owner_id=friend_id, friend_id=user_id, msg_id=msg_id)


def handle_message_is_distributed_request(server, conn, user_id, friend_id, msg_id):
    from chatting.function import find_logged_in_user
    from database.chatting_databases import edit_message_to_distributed

    bool_value, friend_connection = find_logged_in_user(server, int(friend_id))
    if bool_value:  # if the user is logged in, we send him directly the response, that his message is seen by the user.
        response = f'message_is_seen/{user_id}/{msg_id}'
        friend_connection.sendall(response.encode('utf-8'))

    edit_message_to_distributed(table_owner_id=user_id, friend_id=friend_id, msg_id=msg_id)  # and we edit both tables.
    edit_message_to_distributed(table_owner_id=friend_id, friend_id=user_id, msg_id=msg_id)


def handle_create_group_request(server, conn, user_id, grp_id, grp_name, friends_ids):
    from SERVER.database.chatting_databases import create_grp_table
    from SERVER.database.users_database import add_friend, add_user
    from SERVER.chatting.function import find_logged_in_user, get_friends_ids_string, encode, decode

    friends_ids = friends_ids.split('-')
    add_user(userid=grp_id, username=encode(grp_name), email=encode('email'), password=encode(123))
    for friend_id in friends_ids:
        bool_value, friend_connection = find_logged_in_user(server, int(friend_id))
        friends_ids_data = get_friends_ids_string(friends_ids, friend_id)
        if bool_value:
            friend_connection.sendall(f'group_is_created/{grp_id}/{grp_name}/{friends_ids_data}'.encode('utf-8'))

        create_grp_table(user_id=friend_id, conv_id=grp_id)
        add_friend(user_id=friend_id, friend_id=grp_id)

    add_friend(user_id=user_id, friend_id=grp_id)
    create_grp_table(user_id=user_id, conv_id=grp_id)
