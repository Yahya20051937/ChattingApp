import sqlite3


class DataBaseManagement:
    def __init__(self, file_name):
        self.file = file_name
        self.connection = None

    def __enter__(self):
        self.connection = sqlite3.connect(self.file, check_same_thread=False)
        cursor = self.connection.cursor()
        return cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val or exc_val or exc_tb:
            self.connection.commit()
            self.connection.close()
        else:
            self.connection.commit()
            self.connection.close()
