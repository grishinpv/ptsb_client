__author__ = "Pavel Grishin"
__version__ = "0.0.0.3"


import re, socket, os
import requests
import builtins
from tabulate import tabulate
from functools import singledispatch

from PTSB_Errors import *
from PTSB_Response import *
from PTSB_Body import *
from PTSB_Statistics import *
from API_Methods import *

DEBUG = False

class PTSBApi(object):
    BASE_API_PATH = "api/v1"

    def __init__(self, api_key, sandbox_ip, proxy_srv='', proxy_port='', proxy_user=None, proxy_pwd=None, disable_cert_checking=True, debug=False):
        builtins.DEBUG = debug
        if not ((type(api_key) == str) and (len(api_key) == 86)):
            raise ValueError("PTSBApi __init__ parameter 'api_key' must be a STRING with valid API key format")
        if not ((type(sandbox_ip) == str) and ((self.__isValidIP(sandbox_ip)) or (self.__isValidHostname(
            sandbox_ip)))):
            raise ValueError("PTSBApi __init__ parameter 'sandbox_ip' must be a STRING that contains a valid IP address or hostname.") 
        
        self.api_key = api_key
        self.sandbox_ip = sandbox_ip
        self.headers = {"X-API-Key": self.api_key}
        self.proxies = self.__getProxy(proxy_srv, proxy_port, proxy_user, proxy_pwd)
        self.statistics = Statistics()
        if disable_cert_checking == True:
            requests.packages.urllib3.disable_warnings() # To disable warning for Self-Signed Certificates
        if self.CheckHealth():
            self.images = self.GetImages()
        
        

    def __getProxy(self, pserver, pport, puser = None, ppass = None):
        proxy_server = pserver
        if proxy_server == '':
            proxies = {'http': '', 'https': ''}
            return proxies
        proxy_port = pport
        proxy_user = puser
        proxy_userpass = ppass
        if proxy_user == None or proxy_userpass == None:
            proxy_line = '{}:{}'.format(proxy_server, proxy_port)
            proxies = {'http': 'http://{}'.format(proxy_line), 'https': 'https://{}'.format(proxy_line),}
        else:
            proxy_line = '{}:{}@{}:{}'.format(proxy_user, proxy_userpass, proxy_server, proxy_port)
            proxies = {'http': 'http://{}'.format(proxy_line), 'https': 'https://{}'.format(proxy_line),}
        return proxies


    def __isValidHostname(self, hostname):
        # TODO: Make a better regex
        return  re.match("^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$", hostname)


    def __isValidIP(self, address):
        try:
            socket.inet_aton(address)
            return True
        except:
            return False


    def __getApiUrl(self, method):
        return "https://{sandbox_ip}/{base_api_path}/{method_path}/{service}".format(sandbox_ip=self.sandbox_ip,
                                                                    service=method,
                                                                    method_path=SUPPORTED_API_METHODS.get(method),
                                                                    base_api_path = self.BASE_API_PATH)


    def __send_request(self, api_method, headers = None, http_method = 'post', body = None):
        assert http_method in ["get", "post", "options", "delete", "head", "put", "patch"]
        if not api_method in SUPPORTED_API_METHODS.keys():
            raise Unsupported("Unsupported API method: {}".format(api_method))

        if not headers:
            headers = self.headers

        url = self.__getApiUrl(api_method)
        r = getattr(requests, http_method)(url = url, verify=False, headers=headers, proxies=self.proxies, data = body)
        
        if r.status_code == 400:
            raise BadAPIRequest("URL:{0}\nErrors:\n{1}".format(
                url,
                "\n".join([str(APIError(dict)) for dict in json.loads(r.text)["errors"]])
            ))
        elif r.status_code == 401:
            raise BadAPIKey("URL:{0}\nErrors:\n{1}".format(
                url,
                "\n".join([str(APIError(dict)) for dict in json.loads(r.text)["errors"]])
            ))
        elif r.status_code == 404:
            raise ObjectNotFound("URL:{0}\nErrors:\n{1}".format(
                url,
                "\n".join([str(APIError(dict)) for dict in json.loads(r.text)["errors"]])
            ))
        elif r.status_code == 405:
            raise BadAPIMethod("URL:{0}\nErrors:\n{1}".format(
                url,
                "\n".join([str(APIError(dict)) for dict in json.loads(r.text)["errors"]])
            ))
        elif r.status_code >= 500:
            raise ServerError()

        return r


    def __withStatisticsWrapper(self, apiname, result, paramDict = None):
        API = getattr(self.statistics.api_usage, apiname)
        self.statistics.Update(API, result, paramDict)

        #return original result
        return result


    def __asyncStatisticsCorrector(self, apiname, result, paramDict = None):
        API = getattr(self.statistics.api_usage, apiname)
        self.statistics.Update(API, result, paramDict, True)


    def GetImages(self):
        apiname = 'getImages'
        return self.__withStatisticsWrapper(apiname, ResponseFactory("ResponseGetImages", (self.__send_request(apiname))))


    def CheckHealth(self):
        apiname = 'checkHealth'
        return self.__withStatisticsWrapper(apiname, ResponseFactory("ResponseCheckHealth", (self.__send_request(apiname))))


    def UploadScanFile(self, file_path):
        assert os.path.isfile(file_path)
        apiname = 'uploadScanFile'
        headers = self.headers
        headers['Content-Type'] = 'application/octet-stream'

        with open(file_path, 'rb') as f:
            return self.__withStatisticsWrapper(apiname, ResponseFactory("ResponseUploadScanFile", (self.__send_request(apiname, headers=headers, body=f.read()))), {"file_path": file_path})


    def CreateScanTask(self, 
                        file_uri, 
                        file_name = None, 
                        async_result = False,
                        short_result = True,
                        analysis_depth = 0,
                        passwords_for_unpack = [],
                        sandbox_enabled = True,
                        sandbox_skip_check_mime_type = False, 
                        sandbox_image_id = None,
                        sandbox_analysis_duration = 60):
        apiname = 'createScanTask'    
        body = ScanTaskBody(file_uri, 
                                file_name, 
                                async_result,
                                short_result,
                                analysis_depth,
                                passwords_for_unpack,
                                sandbox_enabled,
                                sandbox_skip_check_mime_type, 
                                sandbox_image_id,
                                sandbox_analysis_duration)
        return self.__withStatisticsWrapper(apiname, ResponseFactory("ResponseCreateScanTask",(self.__send_request(apiname, body=body.toJSON()))), {"file_uri": file_uri})


    def CreateScanTaskSimple(self, file_uri, file_name, sandbox_image_id, short_result =False, **kwargs):
        apiname = 'createScanTask'
        body = ScanTaskBodyDefault(file_uri, file_name, sandbox_image_id, short_result, **kwargs)
        body_str = body.toJSON()
        return self.__withStatisticsWrapper(apiname, ResponseFactory("ResponseCreateScanTask", (self.__send_request(apiname, body=body_str))), {"file_uri": file_uri})
    

    def CreateScanTaskSimpleAsync(self, file_uri, file_name, sandbox_image_id, short_result = False, **kwargs):
        apiname = 'createScanTask' 
        body = ScanTaskBodyAsyncDefault(file_uri, file_name, sandbox_image_id, short_result, **kwargs)
        body_str = body.toJSON()
        return self.__withStatisticsWrapper(apiname, ResponseFactory("ResponseCreateScanTask", (self.__send_request(apiname, body=body_str))), {"file_uri": file_uri})


    def CheckTask(self, scan_id, **kwargs):
        apiname = 'checkTask' 
        body = CheckTaskBody(scan_id)
        res = self.__withStatisticsWrapper(apiname, ResponseFactory("ResponseCheckTask", (self.__send_request(apiname, body=body.toJSON()))))
        
        return res


    def GetReport(self, scan_id):
        apiname = 'report'

        if isinstance(scan_id, Response):
            scan_id = scan_id.scan_id
        body = CheckTaskBody(scan_id)
        res = self.__withStatisticsWrapper(apiname, ResponseFactory("ResponseCheckTask", (self.__send_request(apiname, body=body.toJSON()))))
        
        return res
      
    
    def ScanFile(self, file_path, doAsync = True, image_id = None, **kwargs):
        if 'sandbox_enabled' in kwargs.keys() and kwargs['sandbox_enabled'] == True and image_id == None:
            image_id = self.images.images[0].image_id
            print("image_id = " + image_id)
        else:
            kwargs['sandbox_enabled'] = False

        upload_res = self.UploadScanFile(file_path)

        if doAsync:
            return self.CreateScanTaskSimpleAsync(upload_res.file_uri, os.path.basename(file_path), sandbox_image_id=image_id, **kwargs)
        
        return self.CreateScanTaskSimple(upload_res.file_uri, os.path.basename(file_path), sandbox_image_id=image_id, **kwargs)


    @singledispatch
    def DownloadArtifact(self, uri: str):
        apiname = 'downloadArtifact'
        body = DownloadArtifactBody(uri)
        body_str = body.toJSON()
        return self.__withStatisticsWrapper(apiname, ResponseFactory("ResponseDownloadArtifact", (self.__send_request(apiname, body=body_str))))


    @DownloadArtifact.register
    def _(self, result: ResponseCreateScanTask):
        return self.DownloadArtifact(result.data['artifacts'][0]['file_info']['file_uri'])


    def GetStatisticsAvailable(self):
        return self.statistics.StatAvailable()


    def GetStatistics(self, stat_type):
        if stat_type not in self.GetStatisticsAvailable():
            raise NotImplementedError('Statisctics method "{0}" is not implemented'.format(stat_type))
        return getattr(self.statistics, stat_type)()     
            
    
    def PrintStatistics(self, stat_type, addEmptyString = True):
        if stat_type not in self.GetStatisticsAvailable():
            raise NotImplementedError('Statisctics method "{0}" is not implemented'.format(stat_type))
        data = getattr(self.statistics, stat_type)()
        print(tabulate( data["data"], headers=data["headers"] ))
        if addEmptyString:
            print()


    def PrintStatisticsAll(self):
        self.PrintStatistics("UsageInfo_api")
        self.PrintStatistics("UsageInfo_summary")
        self.PrintStatistics("UsageInfo_ext")
        self.PrintStatistics("UsageInfo_mime")
        self.PrintStatistics("UsageInfo_files")
        self.PrintStatistics("UsageInfo_verdicts")
        

    def __str__(self):
        return self.PrintStatisticsAll()
