import subprocess
import threading
import json
import os
import argparse
import re
import threading
import time


def ping(ip_address,time_test):
    command = f"docker exec IperfClient ping {ip_address} -c {time_test}"

    # รันคำสั่ง ping
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # แปลงผลลัพธ์เป็น string
    output = result.stdout.decode('utf-8')

    # ใช้ regular expression เพื่อดึงค่า max round-trip time
    match = re.search(r"min/avg/max = (\d+\.\d+)/(\d+\.\d+)/(\d+\.\d+)", output)

    if match:
        min_val, avg_val, max_val = match.groups()
        print(f"Max round-trip time: {max_val} ms")
        # return {"min": min_val, "avg": avg_val, "max": max_val}
        return {"max": max_val}
    
    else:
        print("ไม่พบข้อมูล round-trip min/avg/max")
        return {"error": "ไม่พบข้อมูล ping"}
    
# ping('192.168.100.100','1')    
print(ping('192.168.100.100','1')   )
