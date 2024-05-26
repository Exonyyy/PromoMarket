class NoSuchUser(Exception):
    def __init__(self):
        Exception.__init__(self)

    def __str__(self):
        return "No such user"
