__author__ = "Pavel Grishin"

'''Supported API methods and method_path'''
SUPPORTED_API_METHODS = {
    'uploadScanFile': "storage",
    'createScanTask': "analysis",
    'checkTask': "analysis",
    'downloadArtifact': "storage",
    'getImages': "engines/sandbox",
    'checkHealth':  "maintenance",
}


class APIMethod(object):
    def __init__(self, name, path):
        self.count = 0
        self.errors = []
        self.name = name
        self.path = path
        self.avg_responstime = 0

    def Update(self, response):
        self.avg_responstime = ((self.avg_responstime * self.count) + response.requestduration) / (self.count + 1)
        self.count += 1

    def __str__(self):
        return ("API name: {}\r\nAPI subpath: {}\r\nUsed: {}\r\nError count: {}\r\nAvg. response time: {}".format(self.name, self.path, self.count, len(self.errors), self.avg_responstime))


class APIMethods(object):
    def __init__(self):
        for k, v in SUPPORTED_API_METHODS.items():
            setattr(self, k, APIMethod(k, v))

    def GetStatistics(self):
        headers = ["API Name", "Use count", "Avg respone time"]
        return {"headers": headers, "data": [[api.name, api.count, api.avg_responstime] for api in [getattr(self, item) for item in self.__dict__.keys()]]}
        
    def Count(self):
        return len(self.__dict__)