import subprocess
import time
import sys
thread_num = sys.argv[1]
interval_time = sys.argv[2]
start_time = '{:.2f}'.format(time.time())
# print(thread_num,start_time)
for i in range(int(thread_num)):
    subprocess.Popen(['python', 'gaze_manipulation_thread.py', start_time, interval_time, str(i),thread_num], universal_newlines=True)
    time.sleep(float(interval_time))
#subprocess.check_output