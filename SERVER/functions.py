def get_request(conn, HEADER, FORMAT):
    data_length = conn.recv(HEADER).decode(FORMAT)
    if data_length:
        data = conn.recv(int(data_length)).decode(FORMAT)
        return data


def find_first_index(lst, element):
    for index, value in enumerate(lst):
        if value == element:
            return index
    return None



