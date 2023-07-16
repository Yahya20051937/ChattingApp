import queue
import random
import threading
import tkinter as tk
from collections import deque
from types import coroutine


def home_page(client, user, send_request_func, user_friends, first=True, data=None):
    from user_authentification.templates import ROOT, displayed_pages
    from client import logger
    from functions import handle_new_page, on_canvas_configure, on_mousewheel, search_object_by_id, get_conversation

    user.page = 'home_page'

    if first:  # if this function is called for the first time, we  get the data from the server

        user.get_friends_data()
        user.get_all_conversations()  # get all the conversations from the server.
        user.get_all_requests()

    friends = user.friends
    all_conversations = user.conversations
    requests = user.friend_requests
    logger.critical(f'{friends}, {all_conversations}, {requests}')

    main_frame = handle_new_page(displayed_pages, ROOT)
    main_frame.pack(fill='both', expand=True)

    commands_frame = tk.Frame(main_frame)
    commands_frame.pack(side='right')

    add_friend_btn = tk.Button(commands_frame, text='friends requests',
                               command=lambda: friends_requests_page(client, user, send_request_func, user_friends,
                                                                     ))
    add_friend_btn.pack(side='top')

    create_group_btn = tk.Button(commands_frame, text='Create group', command=lambda: create_group_page(user))
    create_group_btn.pack(side='top')

    # Create the label
    label = tk.Label(main_frame, text=f'Welcome, {user.username}', borderwidth=2, relief=tk.SOLID)
    label.pack()

    # Create the canvas inside the left frame
    canvas = tk.Canvas(main_frame)
    canvas.pack(side='left', fill='y', expand=True)

    # Create a scrollable frame inside the canvas
    scrollable_frame = tk.Frame(canvas)
    scrollable_frame.pack()

    contacts_frame = tk.Frame(main_frame)
    contacts_frame.pack(side='left', fill='y', expand=True)

    # Create a scrollbar for the canvas
    scrollbar = tk.Scrollbar(main_frame, orient='vertical', command=canvas.yview)
    scrollbar.pack(side='right', fill='y')

    # Configure the canvas to work with the scrollbar
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind("<Configure>", lambda event: on_canvas_configure(canvas, event))
    canvas.bind_all("<MouseWheel>", lambda event: on_mousewheel(canvas, event))

    canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
    scrollable_frame.bind("<Configure>", lambda event: on_canvas_configure(canvas, event))

    conversation_frame = tk.Frame(scrollable_frame)
    conversation_frame.pack(side='right', fill='both', expand=True)

    messages_frame = tk.Frame(conversation_frame)
    messages_frame.pack(side='top', fill='both', expand=True)

    # Add user friends buttons to the scrollable frame

    users_labels, messages_frames = display_conversations_labels(user=user, contacts_frame=contacts_frame,
                                                                 conversation_frame=conversation_frame,
                                                                 messages_frame=messages_frame, messages_frames=[],
                                                                 send_request_func=send_request_func,
                                                                 users_labels=[])

    page_elements_dict = {
        'main_frame': main_frame,
        'commands_frame': commands_frame,
        'add_friend_btn': add_friend_btn,
        'label': label,
        'canvas': canvas,
        'scrollable_frame': scrollable_frame,
        'contacts_frame': contacts_frame,
        'scrollbar': scrollbar,
        'conversation_frame': conversation_frame,
        'messages_frame': messages_frame,
        'users_labels': users_labels,
        'messages_frames': messages_frames
    }
    user.page_elements = page_elements_dict

    thread1 = threading.Thread(target=user.get_responses,
                               )  # start the thread that get messages from the server
    thread1.start()


def friends_requests_page(client, user, send_request_func, user_friends,
                          ):
    from objects import Conversation
    from user_authentification.templates import ROOT, displayed_pages
    from functions import handle_new_page

    user.page = 'friends_requests_page'

    main_frame = handle_new_page(displayed_pages, ROOT)
    main_frame.pack(fill='both', expand=True)

    home_page_button = tk.Button(main_frame, text='Home page',
                                 command=lambda: home_page(client, user, send_request_func, user_friends, first=False,
                                                           ))
    home_page_button.pack(side='left')

    insert_frame = tk.Frame(main_frame)
    insert_frame.pack(fill='x', expand=True)

    response_label = tk.Label(main_frame, text='')
    response_label.pack(side='top')
    user.response_label = response_label

    username = tk.StringVar()

    username_label = tk.Label(insert_frame, text='username:   ')
    username_entry = tk.Entry(insert_frame, textvariable=username)
    submit_button = tk.Button(insert_frame, text='send request',
                              command=lambda: [send_request_func.send(f'/add_friend/{user.id}/{username.get()}'),
                                               ])  # send a request to the server through a coroutine

    username_label.pack(side='left')
    username_entry.pack(side='left')
    submit_button.pack(side='left')

    friend_requests_frame = tk.Frame(main_frame)
    friend_requests_frame.pack(fill='y', expand=True)

    for friend_request in user.friend_requests:  # display the requests
        friend_request.display(friend_requests_frame, send_request_func)


def create_group_page(user):
    from functions import add_friend_to_grp, list_to_string
    from objects import GroupConversation
    from user_authentification.templates import ROOT, displayed_pages

    from functions import handle_new_page, search_object_by_id

    user.page = 'create_group_page'

    main_frame = handle_new_page(displayed_pages, ROOT)
    main_frame.pack(fill='both', expand=True)

    home_page_button = tk.Button(main_frame, text='Home page',
                                 command=lambda: home_page(user.connection, user, user.send_request_func, user.friends,
                                                           first=False,
                                                           ))
    home_page_button.pack(side='left')

    grp_name_frame = tk.Frame(main_frame)
    grp_name_frame.pack(fill='x', expand=True)
    grp_name_label = tk.Label(grp_name_frame, text='Enter the group name:     ')
    group_name = tk.StringVar()
    grp_name_label.pack(side='left')
    grp_name_entry = tk.Entry(grp_name_frame, textvariable=group_name)
    grp_name_entry.pack(side='left')

    response_label = tk.Label(main_frame, text='')
    insert_frame = tk.Frame(main_frame)
    insert_frame.pack(fill='both', expand=True)
    added_friends = []
    username = tk.StringVar()
    username_label = tk.Label(insert_frame, text='username:   ')
    username_entry = tk.Entry(insert_frame, textvariable=username)
    add_button = tk.Button(insert_frame, text='add',
                           command=lambda: add_friend_to_grp(user=user, friend_username=username.get(),
                                                             response_label=response_label,
                                                             added_friends=added_friends))
    response_label = tk.Label(main_frame, text='')

    username_label.pack(side='left')
    username_entry.pack(side='left')
    add_button.pack(side='left')

    response_label.pack()
    submit_button = tk.Button(main_frame, text='Submit',
                              command=lambda conv_id=random.randint(44, 64646): [
                                                                                 user.send_request_func.send(
                                                                                     f'/create_group/{user.id}/{conv_id}/{group_name.get()}/{list_to_string(added_friends)}'),
                                                                                 user.conversations.append(
                                                                                     GroupConversation(user=user,
                                                                                                       name=group_name.get(),
                                                                                                       conv_id=conv_id,
                                                                                                       friends=[
                                                                                                           search_object_by_id(
                                                                                                               user.friends,
                                                                                                               target_id)
                                                                                                           for target_id
                                                                                                           in
                                                                                                           added_friends],
                                                                                                       messages=[])),
                                                                                 user.groups_names.append(
                                                                                     group_name.get())])
    submit_button.pack()


def display_conversations_labels(user, contacts_frame, conversation_frame, messages_frame, messages_frames,
                                 send_request_func, users_labels):
    from objects import UserLabel, GroupConversation
    from functions import handle_new_page, on_canvas_configure, on_mousewheel, search_object_by_id, get_conversation, \
        update_current_conversation
    for label in users_labels:
        label.destroy()

    for conversation in user.conversations:
        if conversation.__class__ == GroupConversation:
            text = conversation.name
        else:
            text = conversation.friend.username

        user_label = UserLabel(master=contacts_frame, conversation=conversation,user=user, name=text, text=text, command=lambda:

        [
            conversation.display(conversation_frame=conversation_frame,
                                 messages_frame=messages_frame,
                                 messages_frames=messages_frames,
                                 func=send_request_func, users_labels=users_labels),

            update_current_conversation(user, conversation)
        ])

        user_label.pack(side='top', padx=5, pady=5)
        users_labels.append(user_label)
    user.page_elements['users_labels'] = users_labels
    return users_labels, messages_frames
