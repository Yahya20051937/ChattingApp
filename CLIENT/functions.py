import tkinter as tk


def handle_new_page(displayed_pages, ROOT):
    try:
        displayed_pages.pop().destroy()
    except IndexError:
        pass

    main_frame = tk.Frame(ROOT)
    main_frame.pack()

    displayed_pages.append(main_frame)
    return main_frame


def split_responses(responses):
    """
    The client may receive multiple response at once, so the goal of this function is to split the response if needed
    for each response component, if it's a response type, we create a list that has all the elements from its index to the next response type index
    finally we add the last response type if there is more that one response
    :param responses:
    :return:
    """
    response_types = [
        'message',
        'friend_request',
        'friend_response',
        'new_conversation',
        'message_is_seen',
        'message_is_distributed',
        'friend_is_online',
        'friend_is_offline'
    ]
    responses_organized = []
    responses_components = responses.split('/')
    index_counter = -1
    skip_next = 0
    last_index_added = None
    for component in responses_components:
        index_counter += 1
        if skip_next > 0:
            skip_next -= 1
            continue
        if component in response_types:
            index_counter2 = index_counter
            for next_component in responses_components[index_counter + 1:]:
                index_counter2 += 1

                if next_component in response_types:
                    response = responses_components[index_counter:index_counter2]
                    skip_next += (index_counter2 - index_counter) - 1
                    last_index_added = index_counter2
                    responses_organized.append(response)
                    break
    try:
        responses_organized.append(responses_components[last_index_added:])
    except IndexError:
        pass
    return responses_organized


def find_index(lst, item):
    for index, value in enumerate(lst):
        if value == item:
            return index
    return -1


def on_canvas_configure(canvas, event):
    canvas.configure(scrollregion=canvas.bbox("all"))


def on_mousewheel(canvas, event):
    canvas.yview_scroll(-1 * int(event.delta / 120), "units")


def search_object_by_id(object_list, target_id):
    for obj in object_list:

        if int(obj.id) == int(target_id):
            return obj
    return None


def search_object_by_object_id(object_list, target_object):
    for obj in object_list:

        if int(obj.id) == int(target_object.id):
            return obj
    return None


def search_object_by_username(object_list, target_object_username):
    for obj in object_list:

        if obj.username == target_object_username:
            return obj
    return None


def get_conversation_by_friend(conversations, friend):
    for conv in conversations:
        if not conv.is_group:
            if int(friend.id) in [int(member.id) for member in conv.members]:
                return conv


def get_label(users_labels, conversation):
    for label in users_labels:
        if int(label.conversation.id) == int(conversation.id):
            return label


def update_current_conversation(user, conversation):
    user.current_conversation = conversation


def delete_friend_request(user, requesting_friend):
    friends_requests = user.friend_requests
    for i in range(len(friends_requests)):
        if friends_requests[i].requesting_user.id == requesting_friend.id:
            user.friend_requests = user.friend_requests[:i] + user.friend_requests[i + 1:]


def change_content(msg_obj, content):
    msg_obj.content = content


def set_id(conversation, msg):
    msg.id = len(conversation.messages) + 1


def add_friend_to_grp(user, friend_username, response_label, added_friends):
    if friend_username in [f.username for f in user.friends]:
        friend_obj = search_object_by_username(user.friends, friend_username)
        if friend_obj.id not in added_friends:
            added_friends.append(friend_obj.id)
            response_label.config(text=f'f{friend_username} added ')
        else:
            response_label.config(text=f'{friend_username} is already in the group !! ')
    else:
        response_label.config(text=f'{friend_username} is not a friend of yours !! ')


def list_to_string(added_friends):
    added_friends_string = ''
    for f in added_friends:
        added_friends_string += f'{f}-'
    if added_friends_string.endswith('-'):
        added_friends_string = added_friends_string[:-1]

    return added_friends_string


def members_usernames(user, members):
    members_as_string = ''
    for member in members:
        if int(member.id) != int(user.id):
            members_as_string += f'{member.username}, '
    if members_as_string.endswith(','):
        members_as_string = members_as_string[:-1]
    return members_as_string


def change_status(user):
    user.status = 'offline'
