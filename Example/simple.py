from PTSB_API import *
import time, os

api_key = ''    # ptsb api
ip = ''         # ptsb ip or fqdn
folder = ''     # folder path with files

client = PTSBApi(api_key, ip)
files_to_scan = [f.path for f in os.scandir(folder) if f.is_file()]
tasks = []      # contains either task or result

doAsync = True # True = выполнить проверки асинхронно, False = выполнить проверки синхронно

for file in files_to_scan:
    
    tasks.append(client.ScanFile(file, doAsync=doAsync))

# if Async wait for the result or skip the step and do smth else
if doAsync:
    while not all(result == True for result in [task.isFinished(client) for task in tasks]):
        # wait 10 sec
        time.sleep(10)

# print statistics
client.PrintStatisticsAll()

# kill api client and cleen up
del client