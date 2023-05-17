from PTSB_API import *
import time, os

api_key = ''    # ptsb api
ip = ''         # ptsb ip or fqdn
folder = ''     # folder path with files

# Sync 
# -----------------------------------
folder = 'D:\\0\\test2'

client = PTSBApi(api_key, ip)
files_to_scan = [f.path for f in os.scandir(folder) if f.is_file()]
tasks = []      # contains all task objects

for file in files_to_scan:
    file_upload_res = client.UploadScanFile(file)

    # wait each task completed 
    # scan within sandbox
    res = client.CreateScanTaskSimple(file_upload_res.file_uri, os.path.basename(file), sandbox_enabled=True, sandbox_image_id=client.images.images[0].image_id)
    #print(res.toJSON())       # print result body

# print statistics
client.PrintStatistics("UsageInfo_api")
client.PrintStatistics("UsageInfo_summary")
client.PrintStatistics("UsageInfo_ext")
client.PrintStatistics("UsageInfo_mime")
client.PrintStatistics("UsageInfo_files")
client.PrintStatistics("UsageInfo_verdicts")

# kill api client and cleen up
del client