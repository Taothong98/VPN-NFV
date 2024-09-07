import paramiko # type: ignore
import subprocess
import json
import datetime
import time
import numpy as np
import scipy.stats
from re import findall
from subprocess import Popen, PIPE
import re

# Configuration
iperf_server_ip = '192.168.191.100'
iperf_client_ip = '192.168.191.121'
ssh_host = '192.168.191.100'
ssh_username = 'gns3'
ssh_password = 'gns3'
iperf_duration = 3  # Duration of iperf test in seconds
iperf_path = r'D:\ProgramIns\iperf3.17_64\iperf3.17_64\iperf3.exe'
project_path = 'D:\Research\CloudFlare'
local_ssh_path = 'C:/Users/philozo/.ssh/id_rsa'
remote_path = '/home/gns3/.ssh/id_rsa.pub'

cpu_utilization = 0
mem_utilization = 0

def ping (host,ping_count, buffer):
    max_rtt = 0
    for ip in host:
        data = ""
        output= Popen(f"ping {ip} -n {ping_count} -l {buffer}", stdout=PIPE, encoding="utf-8")

        for line in output.stdout:
            data = data + line
            ping_test = findall("TTL", data)

        if ping_test:
            print(f"{ip} : Successful Ping")
            avgRTT=re.search("Minimum = (\d+)ms, Maximum = (\d+)ms, Average = (\d+)", str(data))
            print(avgRTT)
            print(avgRTT[2])
            max_rtt = avgRTT[2]
        else:
            print(f"{ip} : Failed Ping")
    return max_rtt

def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    # print(data)
    # print(a)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
    return round(m,2), round(m-h,2), round(m+h,2)

def get_keygen():
    # Construct the SCP command
    scp_command = [
        'scp',f'{ssh_username}@{ssh_host}:{remote_path}',
        local_ssh_path
    ]

    # Execute the SCP command
    try:
        subprocess.run(scp_command, check=True)
        print("File transfer successful!")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

def run_iperf_test():
    """Run iperf3 client command."""
    # cmd = [iperf_path, '-c', iperf_server_ip, "-u", '-t', str(iperf_duration)]
    # process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # # print(process)
    # stdout, stderr = process.communicate()
    # # print(stdout)
    # if process.returncode != 0:
    #     raise Exception(f"iperf3 failed: {stderr.decode()}")
    # return stdout.decode()
    command = ["./iperf3/iperf3", "-c", iperf_server_ip, "-u", "-t", str(iperf_duration), "-J"]
    result = subprocess.run(command, capture_output=True, text=True)
    # print('', result)
    if result.returncode == 0:
        return json.loads(result.stdout)
    else:
        raise Exception(f"iperf3 command failed: {result.stderr}")

def get_cpu_utilization():
    """Connect to Ubuntu server via SSH and get CPU utilization."""
    # client = paramiko.SSHClient()
    # client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # client.connect(ssh_host, username=ssh_username, password=ssh_password)
    
    # stdin, stdout, stderr = client.exec_command("mpstat -P ALL 1 1 | grep \"all\" | awk \'NR==1 {print $5}\'")
    # stdin, stdout, stderr = client.exec_command("mpstat -P ALL 1 1")
    # command = "mpstat -P ALL 1 1 | grep \"all\" | awk \'NR==1 {print $5}\'"
    command = "mpstat -P ALL 1 1" #  | awk \'/all/ {print $5; exit}\'
    ssh_command = f"ssh -i {local_ssh_path} {ssh_username}@{ssh_host} {command}"
    result = subprocess.run(ssh_command, shell=True, capture_output=True, text=True)
    # print('CPU Output : ', result)
    if result.returncode == 0:
        output = result.stdout.splitlines()
        for line in output:
            if 'all' in line and 'Average' not in line:
                columns = line.split()
                sys_percentage = columns[3]
                print(f"%sys for 'all': {sys_percentage}")
                break
    else:
        print(f"Error: {result.stderr}")
    return sys_percentage

# def save_to_json():
#     """Save CPU utilization to a JSON file."""
#     timestamp = datetime.datetime.now().strftime('%y%m%d_%H%M_%S_%f')
#     filename = ''.join([project_path,'Performance',timestamp,'.json'])
#     print(filename)
    
#     data = {
#         'timestamp': timestamp,
#         'cpu_utilization': cpu_utilization,
#         'mem_utilization': mem_utilization       
#     }
    
#     with open(filename, 'w') as file:
#         json.dump(data, file, indent=4)
    
#     print(f"Saved to {filename}")

def get_memory_utilization():
    command = "free -k" # {print $2, $3}'" #  | awk \'/all/ {print $5; exit}\'
    ssh_command = f"ssh -i {local_ssh_path} {ssh_username}@{ssh_host} {command}"
    result = subprocess.run(ssh_command, shell=True, capture_output=True, text=True)
    # Run the htop command and get the output
    mem_output = result.stdout.split('\n')

    TotalMEM = 0; UsedMEM = 0        
    for line in mem_output:
        if line.startswith('Mem:'):
            columns = line.split()
            TotalMEM = int(columns[6])
            UsedMEM = int(columns[2])

    # print(f"TotalMEM: {TotalMEM}")
    # print(f"UsedMEM: {UsedMEM}")
    mem_utilization = (UsedMEM/TotalMEM)*100
    return mem_utilization

def extract_metrics(iperf3_data, cpuutil, memutil, latency, packloss):
    metrics = {}
    end = iperf3_data.get('end', {})
    sum_data = end.get('sum', {})
    if end and sum_data:
        metrics['throughput'] = sum_data.get('bits_per_second', 0)
        metrics['jitter'] = sum_data.get('jitter_ms', 0)
        # metrics['packet_loss'] = sum_data.get('lost_percent', 0)
        # metrics['rtt'] = end.get('round_trip_times', {}).get('mean', 0)
        # metrics['test_duration'] = end.get('test_start', {}).get('duration', 0)
    metrics['cpu_utilization'] = cpuutil
    metrics['mem_utilization'] = memutil
    metrics['latency'] = latency
    metrics['packet_loss'] = packloss
    return metrics

def save_metrics_to_file(metrics):
    timestamp = datetime.now().strftime("%y%m%d_%H%M_%S_%f")
    filename = ''.join([project_path,'\Performance',timestamp,'.json'])
    print(filename)
    with open(filename, 'w') as f:
        print('Dumping ...')
        json.dump(metrics, f, indent=4)

def main():
    try:

        iperf3_data = run_iperf_test()
        metrics = extract_metrics(iperf3_data)
        # save_metrics_to_file(metrics)
        # print(f"Metrics saved to file: {metrics}")

        # # get_keygen()
        # # Run iperf test
        # print("Running iperf test...")
        # iperf_output = run_iperf_test()
        # # print(iperf_output)
        # print("iperf test completed.")
        
        # Get CPU utilization
        print("Getting CPU utilization...")
        cpu_utilization = float(get_cpu_utilization())
        cpu_utilization = cpu_utilization*100
        print(f"CPU Utilization: {cpu_utilization}%")
        
        mem_utilization = get_memory_utilization()
        print(f"MEM Utilization: {mem_utilization}%")
        save_metrics_to_file(metrics, cpu_utilization, mem_utilization)
        print(f"Metrics saved to file: {metrics}")
        
        # save_to_json()       
        time.sleep(30)
            
    except Exception as e:
        print(f"Error: {e}")

    # for i in range(2):
    #     try:
    #         iperf3_data = get_iperf3_data(server_ip)
    #         metrics = extract_metrics(iperf3_data)
    #         save_metrics_to_file(metrics)
    #         print(f"Metrics saved to file: {metrics}")
    #     except Exception as e:
    #         print(f"Error: {e}")
    #     time.sleep(30)

if __name__ == "__main__":
    main()
