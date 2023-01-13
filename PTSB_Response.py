__author__ = "Pavel Grishin"

import requests, json, tempfile

from PTSB_Errors import *
from PTSB_Data import *


class Response(object):
    def __init__(self, r):
        assert issubclass(r.__class__, requests.models.Response)
        self.status_code = r.status_code
        self.requestduration = r.elapsed.total_seconds()
        bodyOject = json.loads(r.text)
        self.data = bodyOject["data"]
        self.errors = [APIError(dict) for dict in bodyOject["errors"]]
    

    def toJSON(self, excludeProperty = ["data"]):
        return json.dumps(self, default=lambda o: {key:value for key, value in o.__dict__.items() if key not in excludeProperty} , 
            sort_keys=True, indent=4)


    def __str__(self):
        return self.toJSON(excludeProperty = [])
    


class ResponseUploadScanFile(Response):
    def __init__(self, r):
        super(ResponseUploadScanFile, self).__init__(r)
        self.file_uri = self.data["file_uri"]
        self.ttl = self.data["ttl"]


class ResponseCreateScanTask(Response):
    def __init__(self, r):
        super(ResponseCreateScanTask, self).__init__(r)
        self.scan_id = self.data["scan_id"]
        self.artifacts = [Artifact(artifact) for artifact in self.data["artifacts"]] if "artifacts" in self.data.keys() else None
        self.result = Result(self.data["result"]) if "result" in self.data.keys() else None


    def isFinished(self, client = None):
        if self.result == None:
            if client == None:
                #false
                return False
            return client.CheckTask(self.scan_id).isFinished()
        else:
            return True
        

class ResponseCheckTask(Response):
    def __init__(self, r):
        super(ResponseCheckTask, self).__init__(r)
        self.scan_id = self.data["scan_id"]
        self.result = Result(self.data["result"]) if "result" in self.data.keys() else None
        #self.artifacts = [Artifact(artifact) for artifact in self.data["artifacts"]]

    def isFinished(self):
        if not "result" in self.__dict__.keys():
            return False
        return (False if self.result == None else True)


class ResponseDownloadArtifact(object):
    def __init__(self, r):
        super(ResponseDownloadArtifact, self).__init__(r)
        tmp_file = tempfile.TemporaryFile()

        with open(tmp_file, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

        self.file_path = tmp_file


class ResponseGetImages(Response):
    def __init__(self, r):
        super(ResponseGetImages, self).__init__(r)
        self.images = [Image(image) for image in self.data]
    
    def Count(self):
        return len(self.images)


class ResponseCheckHealth(Response):
    def __init__(self, r):
        super(ResponseCheckHealth, self).__init__(r)
        self.status = self.data["status"]
    
    def isOnline(self):
        return (True if self.status.lower() == "ok" else False)