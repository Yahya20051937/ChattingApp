def find_logged_in_user(server, user_id):
    logged_in_users = server.log_in_users
    for i in range(len(logged_in_users)):

        if user_id == logged_in_users[i][1]:
            # if the id is present in the list, we return True, along with the user connection
            user_connection = logged_in_users[i][0]
            return True, user_connection
    return False, None  # if not we return False, and NO


def get_members_data_as_string(members_data, member_id):
    data_as_string = ''
    for data in members_data:
        if int(data[0]) != int(member_id):
            data_as_string += f'{data[0]}-{data[1]}>'
    if data_as_string.endswith('>'):
        data_as_string = data_as_string[:-1]
    return data_as_string


encoding_dict = {'a': "'3,9 5'6l9,1,9n1'0'4x1b9'", 'b': "y3,0'3,3 2 1,6'9,0'2'4 4 ", 'c': " 8 8'1'2a1 6 911s5'2 8'5 ",
                 'd': "'6,2'1'9,0'2,1 3 3,9'9,6,", 'e': " 8,4'5'4'4 3 2 2,7'6w1w8'", 'f': ",1 1g5,6 729 4 1'9 7o9'5,",
                 'g': "d8'6h6 5 9'1 7 9x486,8 6d", 'h': ",4s7'7,413 8 2'1,9x3'9'1c", 'i': " 8'6x4'9t4,7 8t4 0,3x210'",
                 'j': "'2'6[2i8b8 5,6 1,2,6 6x8'", 'k': "59'8i9m3 9w2g9'3'5,2g7'8,", 'l': "19,5y1 792 5'6 3,8n3'6'15",
                 'm': " 6,7i5 3,6,0'5b2,8,6]3 5 ", 'n': ",1 3 5u9k6l6'3x3 5,6'8a2,", 'o': ",8 4'8'4,6a5,1l3'2 599'0 ",
                 'p': "'4'9'2,3'6 0d3'3,7'4,6'1'", 'q': ",7,5'6'5e6'6'2,799'5 1 3,", 'r': "87 3v4'6,3'9,5 7,5'4'8,5'",
                 's': "'6'226'4o3'3'093'536'3'8 ", 't': " 4q9,7,7s8m6'5,7 6'8'8,7,", 'u': "w0'6m5,5,7'0b3,4'9'2 1'9,",
                 'v': ",5g9'3,4,6'0 8,5 8'4b1 6'", 'w': "'951,3,7'9,0j8'9 1'8f1,0,", 'x': "n7,0v2 0 0'5'3,6 3 6,6'9'",
                 'y': "l5'7,6d9j4,3'0'8 0a5c4 8,", 'z': " 3 5'6,6 2]9m6'4y7a9 9,5'", '0': "'5x2 7'9 7,3p6v3,0 4k833 ",
                 '1': "5315,9'8 5,2 5'3 1 2'0'7'", '2': ",1'8,1 0 4'8'7'8'0 9'4'9 ", '3': "'8,4,747,7'8'9'2 6,1'3'5n",
                 '4': "k0f0,2[3,8 9'4'5,7m6'7'4 ", '5': ",4'6'9'5'1,811 7,7'2,0,4,", '6': "'4 4 9 2'0c9'3 3c8p1g0,3p",
                 '7': "u3'1b7'8'3,8,5'3'2 7'3,8'", '8': "'2,2,1 7]6 6,7 695p3,8,0 ", '9': "'4'0,1'3 6,5'1,1u9'8s2l0 "}
decoding_dict = {"'3,9 5'6l9,1,9n1'0'4x1b9'": 'a', "y3,0'3,3 2 1,6'9,0'2'4 4 ": 'b', " 8 8'1'2a1 6 911s5'2 8'5 ": 'c',
                 "'6,2'1'9,0'2,1 3 3,9'9,6,": 'd', " 8,4'5'4'4 3 2 2,7'6w1w8'": 'e', ",1 1g5,6 729 4 1'9 7o9'5,": 'f',
                 "d8'6h6 5 9'1 7 9x486,8 6d": 'g', ",4s7'7,413 8 2'1,9x3'9'1c": 'h', " 8'6x4'9t4,7 8t4 0,3x210'": 'i',
                 "'2'6[2i8b8 5,6 1,2,6 6x8'": 'j', "59'8i9m3 9w2g9'3'5,2g7'8,": 'k', "19,5y1 792 5'6 3,8n3'6'15": 'l',
                 " 6,7i5 3,6,0'5b2,8,6]3 5 ": 'm', ",1 3 5u9k6l6'3x3 5,6'8a2,": 'n', ",8 4'8'4,6a5,1l3'2 599'0 ": 'o',
                 "'4'9'2,3'6 0d3'3,7'4,6'1'": 'p', ",7,5'6'5e6'6'2,799'5 1 3,": 'q', "87 3v4'6,3'9,5 7,5'4'8,5'": 'r',
                 "'6'226'4o3'3'093'536'3'8 ": 's', " 4q9,7,7s8m6'5,7 6'8'8,7,": 't', "w0'6m5,5,7'0b3,4'9'2 1'9,": 'u',
                 ",5g9'3,4,6'0 8,5 8'4b1 6'": 'v', "'951,3,7'9,0j8'9 1'8f1,0,": 'w', "n7,0v2 0 0'5'3,6 3 6,6'9'": 'x',
                 "l5'7,6d9j4,3'0'8 0a5c4 8,": 'y', " 3 5'6,6 2]9m6'4y7a9 9,5'": 'z', "'5x2 7'9 7,3p6v3,0 4k833 ": '0',
                 "5315,9'8 5,2 5'3 1 2'0'7'": '1', ",1'8,1 0 4'8'7'8'0 9'4'9 ": '2', "'8,4,747,7'8'9'2 6,1'3'5n": '3',
                 "k0f0,2[3,8 9'4'5,7m6'7'4 ": '4', ",4'6'9'5'1,811 7,7'2,0,4,": '5', "'4 4 9 2'0c9'3 3c8p1g0,3p": '6',
                 "u3'1b7'8'3,8,5'3'2 7'3,8'": '7', "'2,2,1 7]6 6,7 695p3,8,0 ": '8', "'4'0,1'3 6,5'1,1u9'8s2l0 ": '9'}


def encode(decoded_data):
    encoded_data = ''
    for n in str(decoded_data):
        encoded_data += encoding_dict[n]
    return encoded_data


def decode(encoded_data):
    decoded_data = ''
    t = 0
    while t + 25 <= len(encoded_data):
        encoded_number = encoded_data[t:t + 25]
        decoded_data += decoding_dict[encoded_number]
        t += 25

    return decoded_data


def split_requests(requests):
    """
    The client may send multiple requests at once, so the goal of this function is to split the requests if needed.
    For each request type, we create a list that has all the elements from its index to the next request type index.
    Finally, we add the last request type if there is more than one request.
    param requests: The concatenated string of multiple requests.
    :return: A list containing individual requests as separate lists.
    """
    requests_types = ['send', 'add_friend', 'accept', 'decline', 'is_seen', 'is_distributed', 'create_group', 'log_out', 'is_online']
    requests_organized = []
    requests_components = requests.split('/')
    index_counter = -1
    skip_next = 0
    last_index_added = None
    for component in requests_components:
        index_counter += 1
        if skip_next > 0:
            skip_next -= 1
            continue
        if component in requests_types:
            index_counter2 = index_counter
            for next_component in requests_components[index_counter + 1:]:
                index_counter2 += 1

                if next_component in requests_types:
                    request = requests_components[index_counter:index_counter2]
                    skip_next += (index_counter2 - index_counter) - 1
                    last_index_added = index_counter2
                    requests_organized.append(request)
                    break
    try:
        requests_organized.append(requests_components[last_index_added:])
    except IndexError:
        pass
    return requests_organized























