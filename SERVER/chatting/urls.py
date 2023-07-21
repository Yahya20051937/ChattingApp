def get_chatting_url(request, conn, server):
    """
    - If the request is a send-text request, we check if the friend is online , if so we send him directly the message, and we send a response to the user that his message has been distributed. and then we add the message to both databases, so as the message can be seen later.
    - If the request is an add-friend request, we first check if the username is in the database, if not we send a response the user is not found, otherwise, we get the username and id from the database,  and we check is the requested user if online, if so we send him directly the friend request. and finally we add the request to both databases, so it can be seen later, and we send a response that the request has been sent.
    - If the request is an accept-request request, we add the friend and user as friends in both rows, we add a new conversation in the conversations' database, and we create a new conversation table. we then check if the friend is online, and we send data to both users
    - If the request is a decline-request request, we just delete the request from the database
    - If the request is an is-seen-message request,we first add the id of the user who has seen the message in the db, then we  check if the message has been seen by all the other members, we check if the sender is online, if so we send him the response.
    - If the request is an is-distributed-message request, we do the same thing.
    - If the request is a create-group request, we add a new conversation in the database, and we get its id, then we create a new conversation table and we send the conversation data to online users
    :param request:
    :param conn:
    :param server:
    :return:
    """
    from chatting.handle_client import handle_send_text_request, handle_add_friend_request, \
        handle_accept_request, \
        handle_decline_request, handle_message_is_seen_request, handle_message_is_distributed_request, \
        handle_create_group_request, handle_log_out_request, handle_is_online_request

    chatting_urls_dict = {'send': handle_send_text_request,
                          'add_friend': handle_add_friend_request,
                          'accept': handle_accept_request, 'decline': handle_decline_request,
                          'is_seen': handle_message_is_seen_request,
                          'is_distributed': handle_message_is_distributed_request,
                          'create_group': handle_create_group_request, 'log_out': handle_log_out_request,
                          'is_online': handle_is_online_request}

    try:
        func = chatting_urls_dict[request.split('/')[0]]
        args = request.split('/')[1:]

        func(server, conn, *args)  # run the corresponded function here
    except KeyError:
        return None
