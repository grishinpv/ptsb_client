__author__ = "Pavel Grishin"

import json
from PTSB_Errors import *


class SandboxBody(object):
    def __init__(self, enabled, skip_check_mime_type, image_id, analysis_duration):
        if enabled and image_id == None:
            raise BadApiMessageFormat("Sandbox enabled but no 'image_id' provided in request")
        self.enabled = enabled
        self.skip_check_mime_type = skip_check_mime_type
        self.image_id = image_id
        self.analysis_duration = analysis_duration

class Options(object):
    def __init__(self, 
                 analysis_depth,
                 passwords_for_unpack, 
                 sandbox_enabled, 
                 sandbox_skip_check_mime_type,
                 sandbox_image_id,
                 sandbox_analysis_duration):
        self.analysis_depth = analysis_depth
        self.passwords_for_unpack = passwords_for_unpack
        self.sandbox = SandboxBody(sandbox_enabled,
                                   sandbox_skip_check_mime_type, 
                                   sandbox_image_id,
                                   sandbox_analysis_duration)


class Body(object):
    def __init__(self):
        pass

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
            

class ScanTaskBody(Body):
    def __init__(self, 
                file_uri, 
                file_name, 
                async_result = False,
                short_result = True,
                analysis_depth = 0,
                passwords_for_unpack = [],
                sandbox_enabled = True,
                sandbox_skip_check_mime_type = False, 
                sandbox_image_id = None,
                sandbox_analysis_duration = 60):
        super(ScanTaskBody, self).__init__()
        self.file_uri = file_uri
        self.file_name = file_name
        self.async_result = async_result
        self.short_result = short_result
        self.options = Options(analysis_depth, 
                                   passwords_for_unpack, 
                                   sandbox_enabled,
                                   sandbox_skip_check_mime_type, 
                                   sandbox_image_id,
                                   sandbox_analysis_duration)

class ScanTaskBodyDefault(ScanTaskBody):
    def __init__(self, file_uri, file_name, sandbox_image_id, short_result = False):
        super(ScanTaskBodyDefault, self).__init__(file_uri, file_name, sandbox_image_id = sandbox_image_id, short_result = short_result)

class ScanTaskBodyAsyncDefault(ScanTaskBody):
    def __init__(self, file_uri, file_name, sandbox_image_id, short_result = False):
        super(ScanTaskBodyAsyncDefault, self).__init__(file_uri, file_name, sandbox_image_id = sandbox_image_id, async_result = True, short_result = short_result)

class CheckTaskBody(Body):
    def __init__(self, scan_id):
        super(CheckTaskBody, self).__init__()
        self.scan_id = scan_id