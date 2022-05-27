__author__ = "Pavel Grishin"

class APIError(object):
    def __init__(self, dict):
        self.message = dict['message']
        self.type = dict['type']

    def __str__(self):
        return "Error type: {}, Message: {}".format(self.type, self.message)

class PTSBError(RuntimeError):
    pass

class BadAPIKey(PTSBError):
    pass

class BadAPIMethod(PTSBError):
    pass

class BadAPIRequest(PTSBError):
    pass

class ObjectNotFound(PTSBError):
    pass

class UnknownError(PTSBError):
    pass

class ServerError(PTSBError):
    pass

class BadApiMessageFormat(PTSBError):
    pass

class Unsupported(PTSBError):
    pass