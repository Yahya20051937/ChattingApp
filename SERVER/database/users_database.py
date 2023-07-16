def create_table():
    from SERVER.database.database_management import DataBaseManagement
    with DataBaseManagement('users_database.db') as cursor:
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS users_database (id int, username text, email text, password text, friends text)')


def add_user(userid, username, email, password):
    from SERVER.database.database_management import DataBaseManagement
    with DataBaseManagement('users_database.db') as cursor:
        cursor.execute('INSERT INTO users_database VALUES(?, ?, ?, ?, ?)', (userid, username, email, password, ''))


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
    from SERVER.chatting.function import decode, encode
    with DataBaseManagement('users_database.db') as cursor:
        cursor.execute('SELECT friends FROM users_database WHERE id = ?', (user_id,))
        data = cursor.fetchall()

        friends_ids = data[0][0].split('/')[
                      :-1]  # we split the friends string and remove the last element because it is an empty string

        friends_data = []
        for friend_id in friends_ids:
            # we get the friend data by id for each friend, and we append the id and the username into a list
            friend_data = get_user(
                    friend_id)
            if friend_data[3] == encode(123):
                friends_data.append((friend_data[0], decode(friend_data[1]), True))  ################################################################################################################
            else:
                friends_data.append((friend_data[0], friend_data[1], False))  # if we get an index error, then the friend is not found, so the id refers to a conversation not to a friend

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
