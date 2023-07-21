import sqlite3


def create_conversation_table(conv_id):
    from SERVER.database.database_management import DataBaseManagement
    with DataBaseManagement(f'chatting_database.db') as cursor:
        table_name = f'table_{conv_id}_'
        cursor.execute(
            f'CREATE TABLE IF NOT EXISTS {table_name} (msg_id int, sender_id int, message text, seen_by text, distributed_to text)')


def add_message(conv_id, msg_id, sender_id, message):
    from SERVER.database.database_management import DataBaseManagement
    with DataBaseManagement(f'chatting_database.db') as cursor:
        table_name = f'table_{conv_id}_'
        cursor.execute(f'INSERT INTO {table_name} VALUES (?, ?, ?, ?, ?)', (msg_id, sender_id, message, 0, 0))


def get_conversation(conv_id):
    from SERVER.database.database_management import DataBaseManagement
    with DataBaseManagement(f'chatting_database.db') as cursor:
        table_name = f'table_{conv_id}_'
        cursor.execute(f'SELECT * FROM {table_name}')
        data = cursor.fetchall()
        return data


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


def increment_message_is_seen(conv_id, msg_id, seen_by_id):
    from SERVER.database.database_management import DataBaseManagement
    with DataBaseManagement(f'chatting_database.db') as cursor:
        table_name = f'table_{conv_id}_'
        cursor.execute(f'SELECT seen_by FROM {table_name} WHERE msg_id = ?', (int(msg_id),))
        seen_by = cursor.fetchall()[0][0]
        seen_by += f'-{seen_by_id}'
        cursor.execute(f'UPDATE {table_name} SET seen_by = ? WHERE msg_id = ?', (seen_by, msg_id))
        return len(seen_by.split('-')[1:])


def increment_message_is_distributed(conv_id, msg_id, distributed_to_id):
    from SERVER.database.database_management import DataBaseManagement
    with DataBaseManagement(f'chatting_database.db') as cursor:
        table_name = f'table_{conv_id}_'
        cursor.execute(f'SELECT distributed_to FROM {table_name} WHERE msg_id = ?', (int(msg_id),))
        distributed_to = cursor.fetchall()[0][0]
        distributed_to += f'-{distributed_to_id}'
        cursor.execute(f'UPDATE {table_name} SET distributed_to = ? WHERE msg_id = ?', (distributed_to, msg_id))
        return len(distributed_to.split('-')[1:])
