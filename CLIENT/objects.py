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
        self.page_elements = dict()
        self.send_request_func = send_request_func
        self.groups_names = []

    def get_friends_data(self):
        friends_data_json = self.connection.recv(4000).decode('utf-8')
        friends_data = json.loads(friends_data_json)

        friends = []
        for user_id in list(friends_data.keys()):
            friend = User(id=user_id, username=friends_data[user_id])
            friends.append(friend)

        self.friends = friends

    def get_all_conversations(self):
        from functions import search_object_by_id
        all_conversations_as_pickle = self.connection.recv(10000)
        all_conversations = pickle.loads(all_conversations_as_pickle)

        for conv in all_conversations:  # get each friend id and conversation from the server and create a dict and store all the dicts in a list

            friend_id = conv[0]

            content = conv[1]

            messages = []
            for data in content:

                msg_id = int(data[0])
                sender = search_object_by_id(self.friends, data[1])
                if sender is None:
                    sender = self
                message = Message(msg_id=msg_id, sender=sender, content=data[2], user=self)
                is_seen = int(data[3])
                is_distributed = int(data[4])

                if is_seen == 0:
                    message.is_seen = False
                elif is_seen == 1:
                    message.is_seen = True

                if is_distributed == 0:
                    message.is_distributed = False  # if the message is not distributed, we have to send to the server that now it is distributed
                    self.send_request_func.send(f'/is_distributed/{self.id}/{friend_id}/{message.id}')
                    time.sleep(0.2)
                elif is_distributed == 1:
                    message.is_distributed = True

                messages.append(message)
            friend = search_object_by_id(self.friends, friend_id)

            conversation = Conversation(user=self, friend=friend, messages=messages)
            self.conversations.append(conversation)

        try:
            self.current_conversation = self.conversations[0]
        except IndexError:
            pass

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
        - If the response is a friend request accepted, we create a user object that has the new friend data, and we redisplay the users labels, so that the new user label is displayed
        - If the response is a message is seen, we get the message that has been seen, by getting the friend and then the conversation, and we update the message
        - If the response is a message is distributed, we do the same thing we did in the case of the message is seen
        :return:
        """
        from functions import search_object_by_id, add_new_message, get_conversation, get_group_conversation
        from chatting.templates import display_conversations_labels
        from client import logger

        while True:
            response = self.connection.recv(1000).decode(
                'utf-8')
            print(response, self.username)
            if response.split('/')[0] == 'message':
                message_dict = json.loads(response.split('/')[1])
                sender = search_object_by_id(self.friends, message_dict['sender'])
                conversation = get_conversation(self.conversations, sender)
                message = Message(msg_id=len(conversation.messages) + 1, sender=sender, content=message_dict['message'],
                                  user=self)

                messages_frame = self.page_elements['messages_frame']
                messages_frames = self.page_elements['messages_frames']
                users_labels = self.page_elements['users_labels']
                try:
                    if self.page == f'conversation:{sender.id}':
                        message.display(messages_frame, messages_frames, func=self.send_request_func)

                    else:
                        message.edit(users_labels)
                except AttributeError:
                    message.edit(users_labels)

                add_new_message(message.sender, message,
                                self.conversations)  # add the new message to the conversations list
            elif response.split('/')[0] == 'grp_message':
                message_dict = json.loads(response.split('/')[2])
                conv_id = response.split('/')[1]
                sender = search_object_by_id(self.friends, message_dict['sender'])
                conversation = get_group_conversation(self.conversations, conv_id)
                message = Message(msg_id=len(conversation.messages + 1), sender=sender, content=message_dict['message'],
                                  user=self)

                messages_frame = self.page_elements['messages_frame']
                messages_frames = self.page_elements['messages_frames']
                users_labels = self.page_elements['users_labels']

                try:
                    if self.page == f'conversation:{sender.id}':
                        message.display(messages_frame, messages_frames, func=self.send_request_func)

                    else:
                        message.edit(users_labels)
                except AttributeError:
                    message.edit(users_labels)

                add_new_message(message.sender, message,
                                self.conversations)  # add the new message to the conversations list
            elif response.split('/')[0] == 'friend_request':
                requesting_user = User(id=response.split('/')[2], username=response.split('/')[1])
                friend_request = FriendRequest(user=self, requesting_user=requesting_user)
                friend_request.display(friend_requests_frame=self.friend_requests_frame,
                                       send_request_func=self.send_request_func)
                self.friend_requests.append(friend_request)
            elif response.split('/')[0] == 'friend_response':
                self.response_label.config(text=response.split('/')[1])

            elif response.split('/')[0] == 'friend_request_accepted':
                new_friend = User(id=response.split('/')[1], username=response.split('/')[2])
                self.friends.append(new_friend)
                new_conversation = Conversation(user=self, friend=new_friend, messages=[])
                self.conversations.append(new_conversation)

                contacts_frame = self.page_elements['contacts_frame']
                conversation_frame = self.page_elements['conversation_frame']
                messages_frame = self.page_elements['messages_frame']

                messages_frames = self.page_elements['messages_frames']
                users_labels = self.page_elements['users_labels']

                display_conversations_labels(user=self, contacts_frame=contacts_frame,
                                             conversation_frame=conversation_frame, messages_frames=messages_frames,
                                             messages_frame=messages_frame, send_request_func=self.send_request_func,
                                             users_labels=users_labels)
            elif response.split('/')[0] == 'message_is_seen':
                friend_id = response.split('/')[1]
                msg_id = response.split('/')[2]

                friend = search_object_by_id(self.friends, friend_id)  # we find the friend using the id
                conversation = get_conversation(self.conversations,
                                                friend)  # then we find the conversation using the friend object
                message = search_object_by_id(conversation.messages, msg_id)  # then we find the message using the id

                message.is_seen = True
                if self.page == f'conversation:{conversation.friend.id}':
                    message.update_is_seen()

            elif response.split('/')[0] == 'message_is_distributed':
                friend_id = response.split('/')[1]
                msg_id = response.split('/')[2]

                friend = search_object_by_id(self.friends, friend_id)  # we find the friend using the id
                conversation = get_conversation(self.conversations,
                                                friend)  # then we find the conversation using the friend object
                message = search_object_by_id(conversation.messages, msg_id)  # then we find the message using the id

                message.is_distributed = True
                if self.page == f'conversation:{conversation.friend.id}':
                    message.update_is_distributed()

            elif response.split('/')[0] == 'group_is_created':
                conv_id = response.split('/')[1]
                grp_name = response.split('/')[2]
                friends_ids_string = response.split('/')[3]
                conversation_friends = []
                for friend_id in friends_ids_string.split('-'):
                    friend = search_object_by_id(self.friends, friend_id)
                    conversation_friends.append(friend)
                group_conversation = GroupConversation(user=self, name=grp_name, friends=conversation_friends,
                                                       messages=[], conv_id=conv_id)
                self.conversations.append(group_conversation)

                contacts_frame = self.page_elements['contacts_frame']
                conversation_frame = self.page_elements['conversation_frame']
                messages_frame = self.page_elements['messages_frame']

                messages_frames = self.page_elements['messages_frames']
                users_labels = self.page_elements['users_labels']

                display_conversations_labels(user=self, contacts_frame=contacts_frame,
                                             conversation_frame=conversation_frame, messages_frames=messages_frames,
                                             messages_frame=messages_frame, send_request_func=self.send_request_func,
                                             users_labels=users_labels)


class Conversation:
    def __init__(self, user, friend, messages):
        self.user = user
        self.friend = friend
        self.messages = messages
        self.friends = None
        self.id = None

    def display(self, conversation_frame, messages_frame, func, messages_frames,
                users_labels):
        from functions import get_label, change_content, set_id

        self.user.page = f'conversation:{self.friend.id}'

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

        if self.__class__ == GroupConversation:
            x = 'grp_send'
            y = ''
            j = self.id
            for f in self.friends[:-1]:
                y += f'{f.id}-'
            y += f'{self.friends[-1]}'
        else:
            x = 'send'
            y = self.friend.id
            j = self.friend.id

        send_button = tk.Button(entry_frame, text='Send',
                                command=lambda message_obj=Message(msg_id=999, user=self.user,
                                                                   sender=self.user,
                                                                   content=None)

                                : [
                                    set_id(self, message_obj),
                                    change_content(message_obj, message.get()),
                                    message_obj.display(
                                        messages_frames=messages_frames, messages_frame=messages_frame, func=func),
                                    self.add_message(
                                        message_obj),

                                    func.send(f'/{x}/{self.user.id}/{j}/{y}/{message_obj.id}/{message.get()}'),

                                    # send the message to the server through a coroutine, and add the message to the list
                                ])

        sender_label.pack(side='right')
        user_entry.pack(side='right', fill='x', expand=True)
        send_button.pack(side='right')

    def add_message(self, message):
        self.messages.append(message)


class Message:

    def __init__(self, msg_id, user, sender, content):
        self.user = user
        self.id = msg_id
        self.sender = sender
        self.content = content

        self.is_seen = False
        self.is_distributed = False
        self.info_label = None

    def display(self, messages_frame, messages_frames, func):
        from functions import search_object_by_id
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
                if self.is_seen is False:
                    self.is_seen = True  # if the message is displayed, then the user is in the home page, then the user has seen the message  (in the case where the friend is the message sender)
                    func.send(f'/is_seen/{self.user.id}/{self.sender.id}/{self.id}')

    def edit(self, users_labels):
        from functions import get_label, get_conversation
        conversation = get_conversation(self.user.conversations, friend=self.sender)
        user_label = get_label(users_labels, conversation=conversation)
        user_label.config(text=f'{self.sender.username}  (New message)')

    def update_is_seen(self):
        self.info_label.config(text='✔✔', fg='skyblue')

    def update_is_distributed(self):
        self.info_label.config(text='✔✔', fg='gray')


class UserLabel(tk.Button):
    def __init__(self, user, conversation, name, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.user = user
        self.conversation = conversation
        self.name = name

    def fix_text(self):
        self.config(text=self.name)


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
                                      command=lambda x=self.requesting_user.id, y=request_frame: [
                                          send_request_func.send(f'/accept/{self.user.id}/{x}'), y.destroy(),
                                          self.user.friends.append(self.requesting_user),
                                          self.user.conversations.append(
                                              Conversation(user=self.user, friend=self.requesting_user, messages=[])),
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


class GroupConversation(Conversation):
    def __init__(self, user, friends, conv_id, name, messages):
        super().__init__(user, None, messages)
        self.friends = friends
        self.id = conv_id
        self.name = name
