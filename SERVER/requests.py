def handle_request(server, request, conn):

    from chatting.urls import get_chatting_url

    from functions import find_first_index
    from user_authentification.urls import get_user_auth_url

    request_dict = {'': [get_user_auth_url, get_chatting_url]}
    value = request_dict[request.split('/')[0]]
    print(request)
    for i in range(len(value)):   # for each function that represent the value of the first part of the request (before the first slash, all the function along with the data as a parameter)
        func = value[i]
        data = request[find_first_index(request, '/') + 1:]

        func(data, conn, server)


