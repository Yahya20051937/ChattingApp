from user_authentification.handle_client import handle_sign_up_request, handle_log_in_request


def get_user_auth_url(request, conn, server):
    user_auth_dict = {'sign_up': handle_sign_up_request, 'log_in': handle_log_in_request}
    try:
        func = user_auth_dict[request.split('/')[0]]
        data = request.split('/')[1]

        func(data, conn, server)
    except KeyError:
        return None
