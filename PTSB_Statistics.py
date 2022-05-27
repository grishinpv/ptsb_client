__author__ = "Pavel Grishin"

import os
import filetype
import datetime
from requests import request
from tabulate import tabulate
from itertools import groupby

from API_Methods import *
from PTSB_Response import *

class ScanResult(object):
    def __init__(self, scan_id, result: Result):
        self.scan_id = scan_id
        self.result = result     

class FileStatInfo(object):
    def __init__(self, file_path):
        assert os.path.isfile(file_path)
        self.id = None
        self.file_ext, self.file_mime = self.guess(file_path)
        self.file_size = os.path.getsize(file_path)
        self.file_uploadtime = 0
        self.file_scantime = 0
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.scans = []
        #self.results = []


    def guess(sel, file_path):
        kind = filetype.guess(file_path)
        if kind is None:
            return "Null", "Null"
        return kind.extension, kind.mime

    def __updateScantime(self, new_scantime):
        if len(self.scans) > 1:
            self.file_scantime = (((self.file_scantime * (len(self.scans) - 1)) + new_scantime) / len(self.scans))
        else:
            self.file_scantime = new_scantime

    def Update_scans(self, scan_id, result):
        scanObj = next((obj for obj in self.scans if obj.scan_id == scan_id), None)
        if scanObj.result == None:
            scanObj.result = result
        
        if not result.duration == None:
            self.__updateScantime(result.duration)

        
       
class Statistics(object):
    def __init__(self):

        #file
        self.file_stats = []
        
        #API usage
        self.api_usage = APIMethods()

    # ------------------------------------
    #region Update stats
    # ------------------------------------
    def Update(self, API: APIMethod, response, paramDict, skipAPIobjUpdate = False):
        assert issubclass(response.__class__, Response)

        #update usage count
        if not skipAPIobjUpdate:
            API.Update(response)

        #update API specific values
        if API.name == "getImages":
            #do nothing
            pass


        elif API.name == "checkHealth":
            #do nothing
            pass


        elif API.name == "uploadScanFile":
            if paramDict == None:
                raise AttributeError("Attribute 'paramDict' not found")
            if "file_path" not in paramDict.keys():
                raise AttributeError("Element 'file_path' is not found in 'paramDict'")

            fileObj = FileStatInfo(paramDict['file_path'])
            fileObj.file_uploadtime = response.requestduration
            fileObj.id = response.file_uri
            self.file_stats.append(fileObj)


        elif API.name == "createScanTask":
            if paramDict == None:
                raise AttributeError("Attribute 'paramDict' not found")
            if "file_uri" not in paramDict.keys():
                raise AttributeError("Element 'file_uri' is not found in 'paramDict'")

            #fileObj = (lambda o: o.id == response.file_uri, self.file_stats)
            fileObj = next((obj for obj in self.file_stats if obj.id == paramDict['file_uri']), None)
            if fileObj == None:
                raise "File with id '{}' was not loaded with this client api".format()

            if response.isFinished():
                if response.result:
                    fileObj.Update_scans(response.scan_id, response.result)
                    #if "duration" in response.result.__dict__.keys():
                    #    if response.result.duration != None:
                    #        fileObj.Update_scantime(float(response.result.duration))
                    #    if not response.scan_id in fileObj.scan_ids:
                    #        fileObj.results.append(response.result)

            #scan_id must be the last to set!
            if not skipAPIobjUpdate:
                fileObj.scans.append(ScanResult(response.scan_id, None))


        elif API.name == "checkTask":
            if (response.isFinished()):
                if response.result:
                    #fileObj = (lambda o: o.scan_id == response.scan_id, self.scan_ids)
                    fileObj = next((obj for obj in self.file_stats if response.scan_id in [o.scan_id for o in obj.scans]), None)
                    #fileObj = next((obj for obj in self.file_stats if response.scan_id in [scanobj.scans for scanobj in self.file_stats]), None)
                    if fileObj == None:
                        raise "File with id '{}' was not loaded with this client api".format()

                    #fileObj.Update_scan(response.scan_id, response.result))
                    fileObj.Update_scans(response.scan_id, response.result)

                    #if "duration" in response.result.__dict__.keys():
                    #    if response.result.duration != None:
                    #        fileObj.Update_scantime(float(response.result.duration))
                    #    if not response.scan_id in fileObj.scan_ids:
                    #        fileObj.results.append(response.result)
    #endregion
    
    # ------------------------------------
    #region GROUP BY 
    # ------------------------------------

    def __GetSortedByParam(self, fList, fParam):
        return sorted(fList, key=lambda item: getattr(item, fParam))


    def __GroupFilesByParam(self, fParam):
        sorted_file_stats = self.__GetSortedByParam(self.file_stats, fParam)
        grouped = {k:list(g) for k, g in groupby(self.file_stats, key=lambda fileitem: getattr(fileitem, fParam))}
        return grouped


    def __GroupFilesByExt(self):
        return self.__GroupFilesByParam("file_ext")

    
    def __GroupFilesByMime(self):
        return self.__GroupFilesByParam("file_mime")   


    def __GroupVerdict(self, fList, fParam):
        grouped = {k:list(g) for k, g in groupby(fList, key=lambda fileitem: getattr(fileitem, fParam))}
        return grouped
    #endregion

    # ------------------------------------
    #region COUNT 
    # ------------------------------------
    def file_count(self):
        return len(self.file_stats)


    def mime_count(self):
        return len(self.__GroupFilesByMime())


    def ext_count(self):
        return len(self.__GroupFilesByExt())


    def mime_item_count(self, mime_type):
        #grouped = self.__GroupFilesByMime()
        return len(self.__GroupFilesByMime()[mime_type])

    
    def ext_item_count(self, mime_type):
        #grouped = self.__GroupFilesByParam("file_mime")
        return len(self.__GroupFilesByMime()[mime_type])
    #endregion

    # ------------------------------------
    #region AVG 
    # ------------------------------------
    def avg_base(self, item_type, attr_name, grouped):

        # item_type - exact ext name or mime_type name
        return (sum([getattr(item, attr_name) for item in grouped[item_type] ])) / len(grouped[item_type])


    def avg_mime_item_size(self, mime_type, grouped = None):
        if grouped == None:
            grouped = self.__GroupFilesByMime()
        return self.avg_base(mime_type, "file_size", grouped)

    
    def avg_ext_item_size(self, ext, grouped = None):
        if grouped == None:
            grouped = self.__GroupFilesByExt()
        return self.avg_base(ext, "file_size", grouped)


    def avg_mime_item_uploadtime(self, mime_type, grouped = None):
        if grouped == None:
            grouped = self.__GroupFilesByMime()
        return self.avg_base(mime_type, "file_uploadtime", grouped)

    
    def avg_ext_item_uploadtime(self, ext, grouped = None):
        if grouped == None:
            grouped = self.__GroupFilesByMime()
        return self.avg_base(ext, "file_uploadtime", grouped)

    def avg_mime_item_scantime(self, mime_type, grouped = None):
        if grouped == None:
            grouped = self.__GroupFilesByMime()
        return self.avg_base(mime_type, "file_scantime", grouped)

    
    def avg_ext_item_scantime(self, ext, grouped = None):
        if grouped == None:
            grouped = self.__GroupFilesByMime()
        return self.avg_base(ext, "file_scantime", grouped)
    #endregion

    # ------------------------------------
    #region USAGE INFO 
    # ------------------------------------

    def UsageInfo_api(self):
        return self.api_usage.GetStatistics()


    def UsageInfo_summary(self):
        return {"data": [
                    ["file count", self.file_count()],
                    ["ext count", self.ext_count()],
                    ["mime count", self.mime_count()]
                ], "headers": [
                    "Name",
                    "Count"
                ]}

    def UsageInfo_ext(self):
        grouped = self.__GroupFilesByExt()
        headers = ["Ext", "Count", "Avg size", "Avg upload time", "Avg scan time"]
        return {"headers": headers, "data": [[k, len(g), self.avg_ext_item_size(k, grouped), self.avg_ext_item_uploadtime(k, grouped),  self.avg_ext_item_scantime(k, grouped)  ] for k, g in grouped.items()]}


    def UsageInfo_mime(self):
        grouped = self.__GroupFilesByMime()
        headers = ["Mime", "Count", "Avg size", "Avg upload time", "Avg scan time"]
        return {"headers": headers, "data": [[k, len(grouped[k]), self.avg_mime_item_size(k, grouped), self.avg_mime_item_uploadtime(k, grouped), self.avg_mime_item_scantime(k, grouped)  ] for k, g in grouped.items()]}


    def UsageInfo_files(self):
        headers = ["File path", "Ext", "Mime", "Size kB", "Upload time", "Scan time", "Scan count", "Last verdict"]
        #return {"headers": headers, "data": [[item.file_path, item.file_ext, item.file_mime, item.file_size, item.file_uploadtime, item.file_scantime, len(item.scan_ids), item.results[-1].verdict ] for item in self.file_stats]}
        return {"headers": headers, "data": [[item.file_path, item.file_ext, item.file_mime, item.file_size, item.file_uploadtime, item.file_scantime, len(item.scans), [res.result for res in item.scans][-1].verdict if [res.result for res in item.scans][-1] != None else "N\A" ] for item in self.file_stats]}

    
    def UsageInfo_verdicts(self):
        verdicts = [i.verdict if i != None else i for i in [item.result for sublist in [fileinfo.scans for fileinfo in self.file_stats] for item in sublist]]
        data = []
        if None in verdicts:
            data.append(["N\A", len([v for v in verdicts if v == None])])
            verdicts = list(filter((None).__ne__, verdicts))
        
        grouped = self.__GroupVerdict(verdicts, "verdict")
        (data.append([ k, len(g) ]) for k, g in grouped.items())
        headers = ["Verdict", "Count"]
        return {"headers": headers, "data": data}
    #endregion

    # ------------------------------------
    # Print 
    # ------------------------------------
    def __str__(self, stat_type):
        if stat_type not in ["UsageInfo_api", "UsageInfo_ext", "UsageInfo_mime", "UsageInfo_summary"]:
            raise ("Failed to print unknown method '{}'".format(stat_type))

        return getattr(self, stat_type)()
    

    # ------------------------------------
    # As JSON 
    # ------------------------------------
    def toJSON(self):
        excludeProperty = []
        return json.dumps(self, default=lambda o: {key:value for key, value in o.__dict__.items() if key not in excludeProperty} , 
            sort_keys=True, indent=4)