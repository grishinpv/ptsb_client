from PTSB_API import *
import time, os

api_key = ''    # ptsb api
ip = ''         # ptsb ip or fqdn
folder = ''     # folder path with files


# Async 
# -----------------------------------

client = PTSBApi(api_key, ip)
files_to_scan = [f.path for f in os.scandir(folder) if f.is_file()]
tasks = []      # contains all task objects

for file in files_to_scan:
    file_upload_res = client.UploadScanFile(file)

    # task will be created immediatly
    # scan within sandbox
    tasks.append(client.CreateScanTaskSimpleAsync(file_upload_res.file_uri, os.path.basename(file), sandbox_enabled=True, sandbox_image_id=client.images.images[0].image_id))
    
# wait for the result or skip the step and do smth else
while not all(result == True for result in [task.isFinished(client) for task in tasks]):
    # wait 10 sec
    time.sleep(10)

# print statistics
client.PrintStatistics("UsageInfo_api")
client.PrintStatistics("UsageInfo_summary")
client.PrintStatistics("UsageInfo_ext")
client.PrintStatistics("UsageInfo_mime")
client.PrintStatistics("UsageInfo_files")
client.PrintStatistics("UsageInfo_verdicts")

# kill api client and cleen up
del client