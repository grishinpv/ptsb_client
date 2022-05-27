__author__ = "Pavel Grishin"

import PTSB_Errors

def _set(value, key):
    return value[key] if key in value.keys() else None

class Result(object):
    def __init__(self, value):
        assert issubclass(value.__class__, dict)
        self.duration = _set(value, "duration")
        self.errors = [PTSB_Errors.APIError(dict_value) for dict_value in value["errors"]]
        self.scan_state = _set(value, "scan_state")
        #threat is only for bad objects
        self.threat = _set(value,"threat")
        self.verdict = _set(value, "verdict")


class FileInfo(object):
     def __init__(self, value):
        assert issubclass(value.__class__, dict)
        self.file_uri = _set(value, "file_uri")
        self.file_path = _set(value, "file_path")
        self.mime_type = _set (value, "mime_type")
        self.md5 = _set(value, "md5")
        self.sha1 = _set(value, "sha1")
        self.sha256 = _set(value, "sha256")
        self.size = _set(value, "size")


class OS(object):
    def __init__(self, value):
        assert issubclass(value.__class__, dict)
        self.name = _set(value, "name")
        self.version = _set(value, "version")
        self.architecture = _set(value, "architecture")
        self.service_pack = _set(value, "service_pack")
        self.locale = _set(value,"locale")


class Image(object):
    def __init__(self, value):
        assert issubclass(value.__class__, dict)
        self.image_id = value["image_id"]
        self.version = value["version"]
        self.os = OS(value["os"])


class SandboxLogs(object):
    def __init__(self, value):
        assert issubclass(value.__class__, dict)
        self.type = _set(value,"type")
        self.file_uri = _set(value,"file_uri")
        self.file_name = _set(value, "file_name")


class Sandbox(object):
    def __init__(self, value):
        assert issubclass(value.__class__, dict)
        self.image = Image(value["image"])
        self.logs = [SandboxLogs(logs) for logs in value["logs"]]
        self.artifacts = [Artifact(artifact) for artifact in value["artifacts"]]


class Detection(object):
    def __init__(self, value):
        assert issubclass(value.__class__, dict)
        self.detect = _set(value, "detect")
        self.threat = _set(value, "threat")


class EngineResult(object):
    def __init__(self, value):
        assert issubclass(value.__class__, dict)
        self.engine_subsystem = _set(value, "engine_subsystem")
        self.engine_code_name = _set(value, "engine_code_name")
        self.engine_version = _set(value, "engine_version")
        # PTSB api bug for ClamAV (doesn't have database_version item, may be only after update )
        self.database_version = _set(value, "database_version")
        self.database_time = _set(value, "database_time")
        self.result = Result(value["result"]) if "result" in value.keys() else None
        self.detections = [Detection(detection) for detection in value["detections"]] if "detections" in value.keys() else None
        # details only exist for sandbox engine
        self.sandbox = Sandbox(value["details"]["sandbox"]) if "details" in value.keys() else None


    
                 

class Artifact(object):
    def __init__(self, value):
        assert issubclass(value.__class__, dict)
        self.type = _set(value, "result")
        self.result = Result(value["result"]) if "result" in value.keys() else None
        self.file_info = FileInfo(value["file_info"]) if "file_info" in value.keys() else None
        self.engine_results = [EngineResult(engine_result) for engine_result in value["engine_results"]] if "engine_results" in value.keys() else None
        self.artifacts = [Artifact(artifacts) for artifacts in value["artifacts"]] if "artifacts" in value.keys() else None