import sqlite3


def create_table(user_id, friend_id):
    from database.database_management import DataBaseManagement
    with DataBaseManagement(f'{user_id}_chat.db') as cursor:
        table_name = f'table_{friend_id}_'
        query = f"CREATE TABLE IF NOT EXISTS {table_name} (msg_id int, sender int, message text, is_seen int, is_distributed int)"

        cursor.execute(query)


def create_grp_table(user_id, conv_id):
    from database.database_management import DataBaseManagement
    with DataBaseManagement(f'{user_id}_chat.db') as cursor:
        table_name = f'table_{conv_id}_'
        query = f"CREATE TABLE IF NOT EXISTS {table_name} (msg_id int, sender int, message text, is_seen int, is_distributed int)"

        cursor.execute(query)


def create_request_table(user_id):
    from database.database_management import DataBaseManagement
    with DataBaseManagement(f'{user_id}_chat.db') as cursor:
        table_name = 'requests_table'
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (id int, username text)")


def get_all_requests(user_id):
    from database.database_management import DataBaseManagement
    with DataBaseManagement(f'{user_id}_chat.db') as cursor:
        cursor.execute('SELECT * FROM requests_table')
        data = cursor.fetchall()
        return data


def add_request(requested_user_id, requesting_user_id, requesting_user_username):
    from database.database_management import DataBaseManagement
    with DataBaseManagement(f'{requested_user_id}_chat.db') as cursor:
        cursor.execute('INSERT INTO requests_table VALUES(?, ?)', (requesting_user_id, requesting_user_username))


def delete_request(user_id, friend_id):
    from database.database_management import DataBaseManagement
    with DataBaseManagement(f'{user_id}_chat.db') as cursor:
        cursor.execute('DELETE FROM requests_table WHERE id = ?', (friend_id,))


def get_conversation(user_id, friend_id):
    from database.database_management import DataBaseManagement
    file_name = f'{user_id}_chat.db'
    with DataBaseManagement(file_name) as cursor:
        table_name = f'table_{friend_id}_'
        query = f'SELECT * FROM {table_name}'
        cursor.execute(query)
        conversation = cursor.fetchall()
        return conversation


def add_message(table_owner_id, friend_id, sender_id, receiver_id, message):
    from server import logger

    """
    if the user is the sender, then his id must represent the sender column in the table along with the message, and if the friend is the sender, we do the opposite
    """
    from database.database_management import DataBaseManagement
    file_name = f'{table_owner_id}_chat.db'
    logger.critical(f'file name: {file_name}')
    with DataBaseManagement(file_name) as cursor:
        table_name = f'table_{friend_id}_'
        msg_id = len(get_conversation(table_owner_id, friend_id)) + 1
        query = f'INSERT INTO {table_name} VALUES (?, ?, ?, 0, 0)'
        try:
            cursor.execute(query, (msg_id, sender_id, message))
        except sqlite3.OperationalError:
            create_table(sender_id, receiver_id)
            create_table(receiver_id, sender_id)


def add_grp_message(table_owner_id, conv_id, sender_id, message):
    from database.database_management import DataBaseManagement
    with DataBaseManagement(f'{table_owner_id}_chat.db') as cursor:
        table_name = f'table_{conv_id}_'
        msg_id = len(get_conversation(user_id=table_owner_id, friend_id=conv_id)) + 1
        cursor.execute(f'INSERT INTO {table_name} VALUES (?, ?, ?, 0, 0)', (msg_id, sender_id, message))


def edit_message_to_seen(table_owner_id, friend_id, msg_id):
    from database.database_management import DataBaseManagement
    file_name = f'{table_owner_id}_chat.db'
    with DataBaseManagement(file_name) as cursor:
        table_name = f'table_{friend_id}_'
        cursor.execute(f'UPDATE {table_name} SET is_seen = ? WHERE msg_id = ?', (1, msg_id))


def edit_message_to_distributed(table_owner_id, friend_id, msg_id):
    from database.database_management import DataBaseManagement
    file_name = f'{table_owner_id}_chat.db'
    with DataBaseManagement(file_name) as cursor:
        table_name = f'table_{friend_id}_'
        cursor.execute(f'UPDATE {table_name} SET is_distributed = ? WHERE msg_id = ?', (1, msg_id))
