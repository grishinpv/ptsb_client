from PTSB_API import *
import time, uuid
from tqdm import tqdm
import argparse
import concurrent.futures
import datetime

#===========================
#        CONSTANTS

api = <API_KEY>

c_proxy = ''
c_proxy_port = ''
c_proxy_usr = None
c_proxy_pwd = None
#===========================


def enum_Files(dest_folder):
    """Enumerate files for processing"""

    fResult = []
    for f_obj in os.scandir(dest_folder):
        if f_obj.is_file():
           fResult.append(f_obj.path)

    return fResult


def upload_Files_ex(connection, file, delay = 0, doAsync=True, sandbox_enabled=False, image_id="win10-1803-x64", debug=False):
    """Upload files to the Sandbox using submit_file_ex"""  

    res = connection.ScanFile(file, doAsync=doAsync, sandbox_enabled=sandbox_enabled, image_id=image_id, debug=debug)
    if res.status_code != 200:
        print('[-] Upload {0} failed. Text = {1}'.format(iter, res.text))
        return False

    time.sleep(delay)

    return True

def upload_Files(connection, file, delay = 0):
    """Upload files to the Sandbox"""

    res = connection.submit_file(file)
    if res.status_code != 200:
        print('[-] Upload {0} failed. Text = {1}'.format(iter, res.text))
        return False

    time.sleep(delay)

    return True

def is_valid_ip(address):
    try:
        socket.inet_aton(address)
        return True
    except:
        return False

def is_valid_hostname(hostname):
    # TODO: Make a better regex
    return  re.match("^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$", hostname)

def normalize_result(val, str_len):
    norm_str = ''
    if (type(val) != str):
        val = str(val)

    if len(val) < str_len:
        norm_str = ' '*(str_len-len(val))

    return (norm_str + val)

if __name__ == '__main__':
    ThreadCount = 1         #for multithread function
    RepeatCount = 1         #repeate file count

    try:
        parser = argparse.ArgumentParser(description='Sandbox API uploader')
        parser.add_argument('-i', '--ip', dest='ip',  required=True, action="store", help='Sandbox ip or hostname')
        parser.add_argument('-f', '--folder', dest='path', required=True, action="store",  help='folder path with files to send')
        parser.add_argument('-d', '--delay', dest='delay', required=False, action="store", help='delay in seconds between send operation')
        parser.add_argument('-m', '--multi', dest='multi', required=False, action="store", help='thread count (default = 1)')
        parser.add_argument('-r', '--repeat', dest='repeat', required=False, action="store", help='repeat same file count (default = 1)')
        parser.add_argument('--sandbox', dest='dosandbox', required=False, action="store_true", help='check with sanbox')
        parser.add_argument('--debug', dest='debug', required=False, action="store_true", help='debug output')
        args = parser.parse_args()
    except Exception as ex:
        raise Exception("Sandbox API Connection failed. Error: {0}".format(str(ex)))

    """ """
    """Validate input parameters"""
    """ """
    if args.ip:
        if not ((is_valid_ip(args.ip)) or (is_valid_hostname(args.ip))):
            raise Exception("Hostname {0} is not valid IP or Hostname".format(args.ip))

    if args.path:
        if not os.path.exists(args.path):
            raise Exception("Folder {0} does not exist".format(args.path))

    if args.delay:
        if not (args.delay.isnumeric() or (re.match(r'^\d+(?:\.\d+)?$', args.delay))):
            raise Exception("Delay value must be numeric of float (ex 0.5), bot got '{0}'".format(args.delay))
        try:
            delay = int(args.delay)
        except ValueError:
            delay = float(args.delay)
    else:
        delay = 0

    if args.multi:
        if not args.multi.isnumeric():
            raise Exception("Parameter -m expect integer number, but got '{0}'".format(args.multi))
        ThreadCount = int(args.multi)

    if args.repeat:
        if not args.repeat.isnumeric():
            raise Exception("Parameter -r expect integer number, but got '{0}'".format(args.repeat))
        if int(args.repeat) <= 0:
            raise Exception("Parameter -r must be grater than 0, but got '{0}'".format(args.repeat))
        RepeatCount = int(args.repeat)

    """ """
    """Prepare environment"""
    """ """
    files = enum_Files(args.path)     #enum files for emulation

    
    connection = PTSBApi(api, args.ip, proxy_srv='', proxy_port='', proxy_user=None, proxy_pwd=None, disable_cert_checking=True, debug=args.debug)

    start_time = time.time()          #init global timer

    """ """
    """Print initial info"""
    """ """
    print('Init Info')
    print("\tPath = {0}".format(args.path))
    print("\tFile count = {0}".format(str(len(files))))
    print("\tDelay = {0}".format(str(delay)))
    print("\tThreadCount = {0}".format(str(ThreadCount)))
    print("\tStart = {0}".format(datetime.datetime.now()))
    print()

    """ """
    """Start upload"""
    """ """
    if args.multi:
        with concurrent.futures.ThreadPoolExecutor(max_workers=ThreadCount) as executor:
            future_upload = []

            print("Prepare jobs")
            for file in tqdm(files):
                for i in range(RepeatCount):
                    if args.dosandbox:
                        future_upload.append(executor.submit(upload_Files_ex, connection, file, delay, True, True))
                    else:
                        future_upload.append(executor.submit(upload_Files_ex, connection, file, delay))
                #future_upload.append(executor.submit(upload_Files, connection, file, delay))       # simple version of submit

            kwargs = {
                'total': len(future_upload),
                'unit': 'upload_Files',
                'unit_scale': True,
                'leave': True
            }

            print("")
            print("Execute jobs")
            for f in tqdm(concurrent.futures.as_completed(future_upload), **kwargs):
                pass
    else:
        
        print("Execute jobs")
        for file in tqdm(files):
            for i in range(RepeatCount):
                if args.dosandbox:
                    upload_Files_ex(connection, file, delay, True, True)
                else:
                    upload_Files_ex(connection, file, delay)
            #upload_Files(connection, file, delay)          # simple version of submit


    total_time = time.time() - start_time

    """ """
    """Print result"""
    """ """
    print("")
    print("\tFinish = {0}".format(datetime.datetime.now()))
    print("")
    print("┌─────────────────────────┬──────────┬──────────┐")
    print("│                         │ executed │   failed │")
    print("├─────────────────────────┼──────────┼──────────┤")
    print("│                requests │{0} │{1} │".format(normalize_result(str(len(files*RepeatCount)), 9), normalize_result("n\a", 9)))
    print("├─────────────────────────┴──────────┴──────────┤")
    #print("│ total run duration: {0} s │".format(normalize_result(total_time, 23)))
    #print("├───────────────────────────────────────────────┤")
    #print("│ average response time: {0} s │".format(normalize_result(connection.resptime_avg, 20)))
    #print("├───────────────────────────────────────────────┤")
    #print("│ maximum response time: {0} s │".format(normalize_result(connection.resptime_max, 20)))
    #print("└───────────────────────────────────────────────┘")
    print("")

    print(connection.PrintStatistics("UsageInfo_api"))
    print(connection.PrintStatistics("UsageInfo_summary"))
    print(connection.PrintStatistics("UsageInfo_ext"))
    print(connection.PrintStatistics("UsageInfo_mime"))
    print(connection.PrintStatistics("UsageInfo_verdicts"))

    
    #for item in connection.resp_err:
    #    print("\tIter:  {0}".format(item["iter"]))
    #    print("\tCode:  {0}".format(item["status_code"]))
    #    print("\tText:  {0}".format(item["text"]))
    #    print("")

        
