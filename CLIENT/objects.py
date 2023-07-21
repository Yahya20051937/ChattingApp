import random
import time
import tkinter as tk
import json
import pickle
from user_authentification.templates import ROOT


class User:
    def __init__(self, id, username, send_request_func=None, connection=None, friends=None, conversations=None,
                 requests=None,
                 response_label=None, friend_requests_frame=None):
        if conversations is None:
            conversations = []
        if requests is None:
            requests = []
        if friends is None:
            friends = []
        self.id = id
        self.username = username
        self.connection = connection
        self.friends = friends
        self.conversations = conversations
        self.friend_requests = requests
        self.response_label = response_label
        self.friend_requests_frame = friend_requests_frame
        self.current_conversation = None
        self.page = None
        self.label = None
        self.page_elements = dict()
        self.send_request_func = send_request_func
        self.status = 'offline'

    def get_friends_data(self):
        friends_data_pickle = self.connection.recv(4000)
        friends_data = pickle.loads(friends_data_pickle)
        print(friends_data)
        for friend_data in friends_data:
            friend_id = int(friend_data[0])
            friend_username = friend_data[1]
            friend_status = friend_data[2]
            friend = User(id=friend_id, username=friend_username)
            friend.status = friend_status
            self.friends.append(friend)

    def get_all_conversations(self):
        from functions import search_object_by_id
        all_conversations_as_pickle = self.connection.recv(10000)

        all_conversations = pickle.loads(all_conversations_as_pickle)

        for conv in all_conversations:
            conv_id = int(conv[0])
            conv_name = conv[1]
            members = conv[2]
            content = conv[3]
            # print(conv_id, conv_name, members, content)
            members_objects = [search_object_by_id(self.friends, int(member_id)) for member_id in members if
                               int(member_id) != int(self.id)]

            if len(members_objects) == 1:
                is_group = False
                conv_name = members_objects[0].username
            else:
                is_group = True
            members_objects.append(self)

            conversation = Conversation(conv_id=conv_id, name=conv_name, user=self, members=members_objects,
                                        messages=[], is_group=is_group)

            for msg in content:
                msg_id = int(msg[0])
                sender = search_object_by_id(conversation.members, int(msg[1]))
                text = msg[2]
                seen_by = msg[3].split('-')[1:]
                distributed_to = msg[4].split('-')[1:]

                message = Message(conversation=conversation, user=self, msg_id=msg_id, sender=sender, content=text)

                if int(sender.id) == int(self.id):
                    if len(seen_by) == len(conversation.members) - 1:
                        message.is_seen = True
                    else:
                        message.is_seen = False

                    if len(distributed_to) == len(conversation.members) - 1:
                        message.is_distributed = True
                    else:
                        message.is_distributed = False
                else:
                    if str(self.id) in seen_by:
                        message.seen_by_user = True
                    else:
                        message.seen_by_user = False

                    if str(self.id) in distributed_to:
                        message.distributed_to_user = True
                    else:
                        message.distributed_to_user = False
                        self.send_request_func.send(
                            f'/is_distributed/{conversation.id}/{message.id}/{message.sender.id}/{self.id}')
                        time.sleep(0.2)
                        message.distributed_to_user = True

                conversation.messages.append(message)
            self.conversations.append(conversation)

    def get_all_requests(self):
        data_as_pickle = self.connection.recv(4000)

        try:
            requests = pickle.loads(data_as_pickle)
        except pickle.UnpicklingError:
            requests = []

        for data in requests:
            requesting_user = User(id=data[0], username=data[1])
            friend_request = FriendRequest(user=self, requesting_user=requesting_user)
            self.friend_requests.append(friend_request)

    def get_responses(self):
        """
        - If the response is a message, we find the sender user object, and then the conversation object, and we either display the message if the conversation is displayed or we edit the label if the another page is displayed
        - if the response is a friend request, we create a friend request object that has a user attribute, and we display it if the requests' page is displayed, and we add it to the requests attribute in the user object
        - if the response is a friend response from the server, we just display it (either the request is sent or the user is not found)
        - If the response is a new conversation request, then our friend request has been accepted, so we create a new conversation using the data from the server (conv_id , members, ..) and we redisplay all the conversations
        - If the response is a message is seen, we get the message that has been seen, using the msg_id and the conv_id
        - If the response is a message is distributed, we do the same thing we did in the case of the message is seen
        :return:
        """
        from functions import search_object_by_id, split_responses, get_conversation_by_friend, get_label
        from chatting.templates import display_conversations_labels, home_page
        from client import logger

        while self.status == 'online':
            try:
                responses = self.connection.recv(1000).decode(
                    'utf-8')
                responses = split_responses(responses)
                print(responses, self.username)
            except ConnectionAbortedError:
                break
            for response in responses:
                if response[0] == 'message':
                    message_dict = json.loads(response[1])
                    conv_id = int(message_dict['conv_id'])
                    sender = search_object_by_id(self.friends, message_dict['sender'])
                    conversation = search_object_by_id(self.conversations, conv_id)
                    message = Message(msg_id=len(conversation.messages) + 1, sender=sender,
                                      content=message_dict['message'],
                                      user=self, conversation=conversation)

                    self.send_request_func.send(
                        f'/is_distributed/{conv_id}/{message.id}/{sender.id}/{self.id}')  # the message id distributed
                    message.distributed_to_user = True

                    messages_frame = self.page_elements['messages_frame']
                    messages_frames = self.page_elements['messages_frames']
                    users_labels = self.page_elements['users_labels']

                    if self.page == f'conversation:{conversation.id}':
                        message.display(messages_frame, messages_frames, func=self.send_request_func)

                    else:
                        message.edit(users_labels)

                    conversation.messages.append(message)
                elif response[0] == 'friend_request':
                    requesting_user = User(id=response[2], username=response[1])
                    friend_request = FriendRequest(user=self, requesting_user=requesting_user)
                    friend_request.display(friend_requests_frame=self.friend_requests_frame,
                                           send_request_func=self.send_request_func)
                    self.friend_requests.append(friend_request)
                elif response[0] == 'friend_response':
                    self.response_label.config(text=response[1])

                elif response[0] == 'new_conversation':
                    conv_id = int(response[1])
                    name = response[2]
                    members = response[3].split('>')[:-1]

                    members_objects = []
                    for member in members:
                        try:
                            user_id = int(member.split('-')[0])
                            username = member.split('-')[1]
                            member_obj = User(id=user_id, username=username)
                            members_objects.append(member_obj)
                            self.friends.append(member_obj)
                        except ValueError:
                            pass
                    if not len(members_objects) > 1:
                        name = members_objects[0].username

                    members_objects.append(self)
                    if len(members_objects) == 2:
                        is_group = False
                    else:
                        is_group = True
                    conversation = Conversation(user=self, conv_id=conv_id, name=name, messages=[],
                                                members=members_objects,
                                                is_group=is_group)
                    self.conversations.append(conversation)

                    if self.page.split(":")[0] == 'conversation' or self.page == 'home_page':
                        home_page(self, first=False)

                elif response[0] == 'message_is_seen':
                    conv_id = response[1]
                    msg_id = response[2]

                    conversation = search_object_by_id(self.conversations, conv_id)
                    message = search_object_by_id(conversation.messages,
                                                  msg_id)  # then we find the message using the id

                    message.is_seen = True
                    if self.page == f'conversation:{conversation.id}':
                        message.update_is_seen()

                elif response[0] == 'message_is_distributed':
                    conv_id = response[1]
                    msg_id = response[2]

                    conversation = search_object_by_id(self.conversations, conv_id)
                    message = search_object_by_id(conversation.messages,
                                                  msg_id)  # then we find the message using the id

                    message.is_distributed = True
                    if self.page == f'conversation:{conversation.id}':
                        message.update_is_distributed()

                elif response[0] == 'friend_is_online':
                    friend_id = response[1]
                    friend = search_object_by_id(self.friends, friend_id)
                    friend.status = 'online'
                    conversation = get_conversation_by_friend(self.conversations, friend)
                    label = get_label(self.page_elements['users_labels'], conversation)
                    label.update_on_off_line()

                elif response[0] == 'friend_is_offline':
                    friend_id = response[1]
                    friend = search_object_by_id(self.friends, friend_id)
                    friend.status = 'offline'


class Conversation:
    def __init__(self, user, members, messages, conv_id, name, is_group):
        self.user = user
        self.members = members
        self.id = conv_id
        self.messages = messages
        self.name = name
        self.is_group = is_group

    def display(self, conversation_frame, messages_frame, func, messages_frames,
                users_labels):
        from functions import get_label, change_content, set_id, members_usernames

        self.user.page = f'conversation:{self.id}'
        self.user.label.config(
            text=f'You, {members_usernames(self.user, self.members)}, {self.id}')

        for msg in messages_frames:
            msg.destroy()

        user_label = get_label(users_labels,
                               self)  # these two line are used to remove the "new message" string from the label after the button is clicked

        user_label.fix_text()

        for message in self.messages:
            frame = tk.Frame(messages_frame)
            frame.pack(fill='x', expand=True)

            message.display(messages_frame, messages_frames, func)

        entry_frame = tk.Frame(conversation_frame)
        entry_frame.pack(side='bottom', fill='x', expand=True)
        messages_frames.append(entry_frame)

        message = tk.StringVar()

        sender_label = tk.Label(entry_frame, text=self.user.username)
        user_entry = tk.Entry(entry_frame, textvariable=message)

        send_button = tk.Button(entry_frame, text='Send',
                                command=lambda message_obj=Message(msg_id=999, user=self.user,
                                                                   sender=self.user,
                                                                   content=None, conversation=self)

                                : [

                                    set_id(self, message_obj),
                                    change_content(message_obj, message.get()),
                                    self.add_message(
                                        message_obj),
                                    time.sleep(0.1),
                                    message_obj.display(
                                        messages_frames=messages_frames, messages_frame=messages_frame, func=func),

                                    func.send(f'/send/{self.user.id}/{self.id}/{message_obj.id}/{message.get()}'),

                                    # send the message to the server through a coroutine, and add the message to the list
                                ])

        sender_label.pack(side='right')
        user_entry.pack(side='right', fill='x', expand=True)
        send_button.pack(side='right')

    def add_message(self, message):
        self.messages.append(message)


class Message:

    def __init__(self, msg_id, user, sender, content, conversation):
        self.user = user
        self.id = msg_id
        self.sender = sender
        self.content = content
        self.conversation = conversation
        self.is_seen = False
        self.is_distributed = False
        self.seen_by_user = False
        self.distributed_to_user = False
        self.info_label = None

    def display(self, messages_frame, messages_frames, func):
        """
        if the user is the sender, we check if our message has been seen by the other members or not, and we update the message info label. If the user is not the sender, we check if the message has been seen by the user, of not we send a request to the server
        :param messages_frame:
        :param messages_frames:
        :param func:
        :return:
        """
        if self.user.page.split(':')[0] == 'conversation':
            frame = tk.Frame(messages_frame)
            frame.pack(fill='x', expand=True)

            sender = self.sender
            sender_label = tk.Label(frame, text=sender.username)
            message_label = tk.Label(frame, text=f'{self.content},     {self.id}')

            if self.is_distributed and not self.is_seen:
                label_text = '✔✔'
                label_color = 'gray'

            elif self.is_seen:
                label_text = '✔✔'
                label_color = 'skyblue'

            else:
                label_text = '✔'
                label_color = 'gray'

            self.info_label = tk.Label(frame, text=label_text, fg=label_color)

            messages_frames.append(frame)
            if int(sender.id) == int(self.user.id):
                sender_label.pack(side='right')
                message_label.pack(side='left', fill='x', expand=True)
                self.info_label.pack(side='left')

            else:
                sender_label.pack(side='left')
                message_label.pack(side='right', fill='x', expand=True)
                # is_seen_label.pack(side='right')
                if self.seen_by_user is False:
                    self.seen_by_user = True
                    func.send(f'/is_seen/{self.conversation.id}/{self.id}/{self.sender.id}/{self.user.id}')
                    time.sleep(0.2)

    def edit(self, users_labels):
        from functions import get_label
        user_label = get_label(users_labels, self.conversation)
        user_label.config(text=f'{self.conversation.name}  (New message)')

    def update_is_seen(self):
        self.info_label.config(text='✔✔', fg='skyblue')

    def update_is_distributed(self):
        self.info_label.config(text='✔✔', fg='gray')


class UserLabel(tk.Button):
    def __init__(self, conversation, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.conversation = conversation
        if not conversation.is_group:
            self.other_member = \
                [member for member in conversation.members if int(member.id) != int(conversation.user.id)][0]
            self.text = f'{self.conversation.name} ({self.other_member.status})'
        else:
            self.text = self.conversation.name

    def fix_text(self):
        self.config(text=self.text)

    def update_on_off_line(self):
        self.text = f'{self.conversation.name} {self.other_member.status}'
        self.fix_text()


class FriendRequest:
    def __init__(self, user, requesting_user):
        self.user = user
        self.requesting_user = requesting_user

    def display(self, friend_requests_frame, send_request_func):
        from functions import delete_friend_request
        if self.user.page == 'friends_requests_page':
            request_frame = tk.Frame(friend_requests_frame)
            request_frame.pack()
            request_label = tk.Label(request_frame, text=self.requesting_user.username)
            accept_button = tk.Button(request_frame, text='Accept',
                                      command=lambda x=self.requesting_user.id, y=request_frame,
                                      : [
                                          send_request_func.send(f'/accept/{self.user.id}/{x}'), y.destroy(),
                                          self.user.friends.append(self.requesting_user),

                                          delete_friend_request(user=self.user,
                                                                requesting_friend=self.requesting_user)])
            decline_button = tk.Button(request_frame, text='Decline',
                                       command=lambda x=self.requesting_user.id, y=friend_requests_frame: [
                                           send_request_func.send(f'/decline/{self.user.id}/{x}'), y.destroy(),
                                           delete_friend_request(user=self.user,
                                                                 requesting_friend=self.requesting_user)])
            request_label.pack(side='left')
            accept_button.pack(side='left')
            decline_button.pack(side='right')



