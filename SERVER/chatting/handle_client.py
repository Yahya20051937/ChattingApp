import pickle
import json


def handle_send_text_request(server, conn, user_id, conv_id, msg_id, message):
    # get the conversation members
    # add the message in the conversation database
    # send the message to the online members
    # send the info to the user tha the message has been distributed, and add that info to the database
    from SERVER.database.users_database import get_conversation_data
    from SERVER.database.chatting_databases import add_message
    from chatting.function import find_logged_in_user

    conversation_data = get_conversation_data(conv_id=conv_id)[1].split('-')
    # print(conversation_data)
    conversation_members = [member_id for member_id in conversation_data if
                            int(member_id) != int(user_id)]
    add_message(conv_id=conv_id, sender_id=user_id, message=message, msg_id=msg_id)

    for member_id in conversation_members:
        bool_value, member_connection = find_logged_in_user(server, int(member_id))
        if bool_value:
            message_dict = {'conv_id': conv_id, 'sender': user_id, 'message': message}
            message_json = json.dumps(message_dict)
            response = f'message/{message_json}'
            member_connection.sendall(response.encode('utf-8'))


def handle_add_friend_request(server, conn, user_id, friend_username):
    from chatting.function import find_logged_in_user
    from SERVER.database.users_database import get_users_data, get_user
    from SERVER.database.chatting_databases import add_request

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
    # add each other as friends in the database
    # delete the request
    # create a new conversation in the database, and send the id the request receiver and to the request sender
    # add a new conversation table in tha database
    from SERVER.database.users_database import add_friend, add_conversation, get_user
    from SERVER.database.chatting_databases import create_conversation_table, delete_request
    from chatting.function import find_logged_in_user

    add_friend(user_id, friend_id)
    add_friend(friend_id, user_id)

    delete_request(user_id, friend_id)

    conv_id, name = add_conversation(members=f'{user_id}-{friend_id}')
    create_conversation_table(conv_id=conv_id)

    username = get_user(user_id, by='id')[1]
    friend_name = get_user(friend_id, by='id')[1]
    #  print(username, friend_name)
    user_response = f'new_conversation/{conv_id}/{name}/{friend_id}-{friend_name}>'  # the username and user id are separated by an - and the members are separated by a >
    friend_response = f'new_conversation/{conv_id}/{name}/{user_id}-{username}>'
    #  print(user_response, friend_response)
    bool_value, friend_connection = find_logged_in_user(server, int(friend_id))
    if bool_value:
        friend_connection.sendall(friend_response.encode('utf-8'))
    bool_value, user_connection = find_logged_in_user(server, int(user_id))
    if bool_value:
        conn.sendall(user_response.encode('utf-8'))


def handle_decline_request(server, conn, user_id, friend_id):
    from SERVER.database.chatting_databases import delete_request
    delete_request(user_id, friend_id)


def handle_message_is_seen_request(server, conn, conv_id, msg_id, sender_id, seen_by_id):
    # add the seen_by_id to the database
    # check if the message is seen by all the receivers, if so send a response to the sender
    from SERVER.database.chatting_databases import increment_message_is_seen
    from SERVER.database.users_database import get_conversation_data
    from chatting.function import find_logged_in_user

    len_seen_by = increment_message_is_seen(msg_id=msg_id, conv_id=conv_id, seen_by_id=seen_by_id)
    len_conversation_members = len(get_conversation_data(conv_id=conv_id)[1].split('-'))
    print(len_seen_by, len_conversation_members)
    if len_seen_by == len_conversation_members - 1:
        bool_value, sender_connection = find_logged_in_user(server, int(sender_id))
        if bool_value:
            response = f'message_is_seen/{conv_id}/{msg_id}'
            sender_connection.sendall(response.encode('utf-8'))


def handle_message_is_distributed_request(server, conn, conv_id, msg_id, sender_id, distributed_to_id):
    # add the distributed_to_id to the database
    # check if the message is distributed by all the receivers, if so send a response to the sender
    from SERVER.database.chatting_databases import increment_message_is_distributed
    from SERVER.database.users_database import get_conversation_data
    from chatting.function import find_logged_in_user

    len_distributed_to = increment_message_is_distributed(msg_id=msg_id, distributed_to_id=distributed_to_id,
                                                          conv_id=conv_id)
    len_conversation_members = len(get_conversation_data(conv_id=conv_id)[1].split('-'))

    if len_distributed_to == len_conversation_members - 1:
        bool_value, sender_connection = find_logged_in_user(server, int(sender_id))
        if bool_value:
            response = f'message_is_distributed/{conv_id}/{msg_id}'
            sender_connection.sendall(response.encode('utf-8'))


def handle_create_group_request(server, conn, user_id, grp_name, members_ids):
    from SERVER.database.users_database import add_conversation, get_user
    from SERVER.database.chatting_databases import create_conversation_table
    from chatting.function import find_logged_in_user, get_members_data_as_string

    conv_id, name = add_conversation(members=f'{members_ids}', name=grp_name)
    create_conversation_table(conv_id=conv_id)

    members_data = []

    for member_id in members_ids.split('-'):
        member_username = get_user(member_id, by='id')[1]
        members_data.append((member_id, member_username))

    for member_id in members_ids.split('-'):
        bool_value, member_connection = find_logged_in_user(server, int(member_id))
        if bool_value:
            response = f'new_conversation/{conv_id}/{name}/{get_members_data_as_string(members_data, member_id)}>'
            member_connection.sendall(response.encode('utf-8'))


def handle_log_out_request(server, conn, user_id):
    from SERVER.database.users_database import get_user_friends
    from chatting.function import find_logged_in_user

    server.log_in_users = [t for t in server.log_in_users if int(t[1]) != int(user_id)]

    user_friends_ids = [friend[0] for friend in get_user_friends(user_id)]
    for friend_id in user_friends_ids:
        bool_value, friend_connection = find_logged_in_user(server, int(friend_id))
        if bool_value:
            friend_connection.sendall(f'friend_is_offline/{user_id}'.encode('utf-8'))


def handle_is_online_request(server, conn, user_id):
    from SERVER.database.users_database import get_user_friends
    from chatting.function import find_logged_in_user

    user_friends_ids = [friend[0] for friend in get_user_friends(user_id)]
    for friend_id in user_friends_ids:
        bool_value, friend_connection = find_logged_in_user(server, int(friend_id))
        if bool_value:
            friend_connection.sendall(f'friend_is_online/{user_id}'.encode('utf-8'))
