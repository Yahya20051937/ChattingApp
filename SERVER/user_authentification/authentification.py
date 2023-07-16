def sign_up_auth(username, email, password, check_password):
    from server import logger
    from database.users_database import get_users_data

    data = get_users_data()
    usernames = [user[1] for user in data]
    logger.info(f'usernames : {usernames}')
    if username in usernames:  # make sure the username has never been used, otherwise return an exception
        return False, 'username already used'

    emails = [user[2] for user in data]
    logger.info(f'emails : {emails}')
    if email in emails:
        return False, 'email already used'

    if password != check_password:
        return False, "The two passwords don't match "

    else:
        return True, len(data) + 1


def log_in_auth(username, password):
    from server import logger
    from database.users_database import get_users_data

    data = get_users_data()
    usernames = [user[1] for user in data]
    passwords = [user[3] for user in data]
    if username not in usernames:
        return False, 'username not found'
    username_index = usernames.index(username)

    if password != passwords[username_index]:
        return False, 'Invalid password'
    return True, 'Welcome back'
