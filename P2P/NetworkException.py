

class FormatException(Exception):
    def __init__(self, err='Input Format Wrong'):
        Exception.__init__(self, err)


class SendException(Exception):
    def __init__(self, err='Not Send All Data'):
        Exception.__init__(self, err)