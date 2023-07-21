def create_table():
    from SERVER.database.database_management import DataBaseManagement
    with DataBaseManagement('users_database.db') as cursor:
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS users_database (id int, username text, email text, password text, friends text, conversations text)')


def create_conversation_data_table():
    from SERVER.database.database_management import DataBaseManagement
    with DataBaseManagement('users_database.db') as cursor:
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS chats_database (id int, name text, members test)')


def add_user(userid, username, email, password, friends=''):
    from SERVER.database.database_management import DataBaseManagement
    with DataBaseManagement('users_database.db') as cursor:
        cursor.execute('INSERT INTO users_database VALUES(?, ?, ?, ?, ?, ?)',
                       (userid, username, email, password, '', ''))


def add_conversation(members: str, name=''):  # returns the id
    from SERVER.database.database_management import DataBaseManagement
    with DataBaseManagement('users_database.db') as cursor:
        cursor.execute('SELECT * FROM chats_database')
        conv_id = len(cursor.fetchall()) + 1
        cursor.execute('INSERT INTO chats_database VALUES(?, ?, ?)', (conv_id, members, name))
        return conv_id, name


def get_conversation_data(conv_id):
    from SERVER.database.database_management import DataBaseManagement
    with DataBaseManagement('users_database.db') as cursor:
        cursor.execute('SELECT * FROM chats_database WHERE id = ?', (conv_id,))
        data = cursor.fetchall()
        return data[0]


def get_users_data():
    from SERVER.database.database_management import DataBaseManagement
    with DataBaseManagement('users_database.db') as cursor:
        cursor.execute('SELECT * FROM users_database')
        data = cursor.fetchall()
        return data


def get_user(user_data, by='id'):
    from SERVER.database.database_management import DataBaseManagement
    with DataBaseManagement('users_database.db') as cursor:
        if by == 'id':
            cursor.execute('SELECT * FROM users_database WHERE id = ?', (user_data,))
        elif by == 'username':
            cursor.execute('SELECT * FROM users_database WHERE username = ?', (user_data,))
        data = cursor.fetchall()
        return data[0]


def get_user_friends(user_id):
    from SERVER.database.database_management import DataBaseManagement
    with DataBaseManagement('users_database.db') as cursor:
        cursor.execute('SELECT friends FROM users_database WHERE id = ?', (user_id,))
        data = cursor.fetchall()

        friends_ids = data[0][0].split('/')[
                      :-1]  # we split the friends string and remove the last element because it is an empty string

        friends_data = []
        for friend_id in friends_ids:
            friend_data = get_user(
                friend_id)  # we get the friend data by id for each friend, and we append the id and the username into a list
            friends_data.append((friend_data[0], friend_data[1]))  # id, username
        return friends_data


def add_friend(user_id, friend_id):
    from server import logger
    from SERVER.database.database_management import DataBaseManagement
    with DataBaseManagement('users_database.db') as cursor:
        cursor.execute('SELECT friends FROM users_database WHERE id = ?', (user_id,))
        data = cursor.fetchall()[0][0]
        logger.critical(
            f'user friends : {data}')  # we get the user friends from the database, and we append the new user id to them
        data += f'{friend_id}/'
        cursor.execute('UPDATE users_database SET friends = ? WHERE id = ?', (data, user_id))


def get_conversation_members(user_id, conv_id):
    from SERVER.database.database_management import DataBaseManagement
    with DataBaseManagement('users_database.db') as cursor:
        cursor.execute('SELECT conversations FROM users_database WHERE id = ?', (user_id,))
        data = cursor.fetchall()[0][0].split('/')
        for conversation in data:
            if int(conversation.split('>')[1]) == int(conv_id):
                members = conversation.split('>')[0].split('-')
                return members
        return []


def get_all_conversations_info():
    from SERVER.database.database_management import DataBaseManagement
    with DataBaseManagement('users_database.db') as cursor:
        cursor.execute('SELECT * FROM chats_database')
        data = cursor.fetchall()
        return data
