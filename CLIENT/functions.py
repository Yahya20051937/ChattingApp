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


def find_index(lst, item):
    for index, value in enumerate(lst):
        if value == item:
            return index
    return -1


def add_new_message(friend, message, all_conversations):
    conversation = get_conversation(all_conversations, friend)
    conversation.messages.append(message)


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


def get_conversation(conversations, friend):
    for conv in conversations:

        if int(conv.friend.id) == int(friend.id):
            return conv


def get_group_conversation(conversations, conv_id):
    for conv in conversations:
        if int(conv.id) == int(conv_id):
            return conv


def get_label(users_labels, conversation):
    for label in users_labels:
        if label.conversation.friend.id == conversation.friend.id:
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
