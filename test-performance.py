import subprocess
import threading
import json
import os
import argparse


# =================== input for iperf test =================
# ip_address = "192.168.100.100"
# time_test = "1"
# bandwidth = "1Gb"
# parallel = "1"
# buffer = "non"

# ====================== link_capacity =================

link_capacity = "800kbps"

# ฟังก์ชัน main ที่เรียกใช้ฟังก์ชันอื่นๆ
def main():

    args = parse_args()       # รับค่าจาก command-line arguments

    # ตั้งค่า variables ที่เปลี่ยนแปลงได้
    ip_address = args.ip_address
    time_test = args.time_test
    bandwidth = args.bandwidth
    parallel = args.parallel
    buffer_size = args.buffer
        
    docker_start()  # ต้องให้ docker_start() ทำงานเสร็จก่อน
    results = {}
    
    # เพิ่มเฉพาะค่าที่ต้องการบันทึกลงใน JSON
    results["arguments"] = {
        "ip_address": ip_address,
        "time_test": time_test,
        "bandwidth": bandwidth
        # "parallel": parallel,  # ค่านี้ไม่ต้องการบันทึกไว้ใน JSON
        # "buffer_size": buffer_size  # ค่านี้ไม่ต้องการบันทึกไว้ใน JSON
    }
    
    # ฟังก์ชันที่ทำงานร่วมกับ threads เพื่อเก็บผลลัพธ์
            
    def run_iperf():
        results["iperf"] = iperf(ip_address, time_test, bandwidth, parallel)  # ส่งค่าพารามิเตอร์ไปให้ iperf()

    def run_getcpu():
        results["cpu"] = getcpu(time_test,)

    def run_getmem():
        results["memory"] = get_memory_usage(time_test,)

    # สร้าง threads สำหรับ iperf, getcpu, และ get_memory_usage
    
    iperf_thread = threading.Thread(target=run_iperf)
    getcpu_thread = threading.Thread(target=run_getcpu)
    getmem_thread = threading.Thread(target=run_getmem)

    # เรียกใช้ทั้งสามฟังก์ชันพร้อมกัน

    iperf_thread.start()
    getcpu_thread.start()
    getmem_thread.start()

    # รอให้ทั้งสามฟังก์ชันเสร็จสิ้นการทำงาน

    iperf_thread.join()
    getcpu_thread.join()
    getmem_thread.join()

    # บันทึกผลลัพธ์ลงไฟล์ JSON
    with open('output.json', 'w') as json_file:
        json.dump(results, json_file, indent=4)

    print("Results saved to output.json")
    
# ฟังก์ชัน parse_args เพื่อรับค่าจาก command-line arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Test performance script")
    
    # =================== input for iperf test =================
    parser.add_argument('-ip', '--ip_address', type=str, default="192.168.100.100", help='IP address to test')
    parser.add_argument('-t', '--time_test', type=str, default="1", help='Test duration in seconds')
    parser.add_argument('-b', '--bandwidth', type=str, default="1Gb", help='Bandwidth for iperf')
    parser.add_argument('-p', '--parallel', type=str, default="1", help='Number of parallel streams for iperf')
    parser.add_argument('-bf', '--buffer', type=str, default="8KB", help='Buffer size for iperf')
    
    # ====================== link_capacity =================
    parser.add_argument('-lc', '--link_capacity', type=str, default="10240kbps", help='link_capacity of VPN-Server')
    
    return parser.parse_args()   
    
def get_shell_output(command):
    # รันคำสั่ง shell และดึงผลลัพธ์กลับมา
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout.strip()    


def set_link_capacity():
    
    command1 = "docker exec VPNserver tc qdisc add dev eth0 root handle 1:0 htb default 10"
    command2 = "docker exec VPNserver tc class add dev eth0 parent 1:0 classid 1:10 htb rate {link_capacity} prio 0"
    command3 = "docker exec VPNserver iptables -A OUTPUT -t mangle -p udp -j MARK --set-mark 10"
    command4 = "docker exec VPNserver tc filter add dev eth0 parent 1:0 prio 0 protocol ip handle 10 fw flowid 1:10"
    
def docker_start():
    # หา path ปัจจุบันที่ไฟล์ Python และ docker-compose.yml อยู่
    current_path = os.getcwd()

    # สร้าง command สำหรับ docker-compose ps โดยระบุ path ของไฟล์ docker-compose.yml
    command = f"docker-compose -f {current_path}/docker-compose.yml ps -a"
    
    restart_docker = f"docker-compose -f {current_path}/docker-compose.yml restart"
    
    # รัน command ที่สร้างขึ้น
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # ตรวจสอบผลลัพธ์
    if result.returncode == 0:
        print("Command executed successfully:\n", result.stdout)

        # แยกบรรทัดข้อมูลจากผลลัพธ์
        lines = result.stdout.splitlines()

        # ตรวจสอบแต่ละบรรทัดที่มีข้อมูล service
        all_up = True
        for line in lines[2:]:  # ข้ามสองบรรทัดแรกที่เป็น header
            if "Up" not in line:  # ถ้า service ไหนไม่ขึ้นว่า Up
                all_up = False
                break

        if all_up:
            print("All services are up.")
        else:
            print("Some services are not running normally!")
            result = subprocess.run(restart_docker, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
    else:
        print("Error executing command:\n", result.stderr)
   
    
# ฟังก์ชัน iperf ใช้ตัวแปร ip_address จากภายนอก
def iperf(ip_address, time_test, bandwidth, parallel):
    # คำสั่งหลักสำหรับ iperf
    command = f"docker exec IperfClient iperf3 -c {ip_address} -u -t {time_test} -b {bandwidth} -P {parallel} > iperf.log"
    
    # รันคำสั่ง iperf และรอให้เสร็จสิ้น
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    if result.returncode != 0:
        return {"error": result.stderr}  # คืนค่าข้อผิดพลาดถ้าเกิดปัญหา

    # รันคำสั่งย่อยหลังจาก iperf เสร็จสิ้น
    senderInterval = "docker exec IperfClient cat /home/iperf/iperf.log | grep -a 'sender' | tail -n 2 | awk '{print $3}' | sed 's/[A-Za-z]*//g'"
    receiverInterval = "docker exec IperfClient cat /home/iperf/iperf.log | grep -a 'receiver' | tail -n 1 | awk '{print $3}' | sed 's/[A-Za-z]*//g'"
    
    senderTransfer = "docker exec IperfClient cat /home/iperf/iperf.log | grep -a 'sender' | tail -n 2 | awk '{print $5}' | sed 's/[A-Za-z]*//g'"
    receiverTransfer = "docker exec IperfClient cat /home/iperf/iperf.log | grep -a 'receiver' | tail -n 1 | awk '{print $5}' | sed 's/[A-Za-z]*//g'"
    
    senderBitrate = "docker exec IperfClient cat /home/iperf/iperf.log | grep -a 'sender' | tail -n 2 | awk '{print $7}' | sed 's/[A-Za-z]*//g'"
    receiverBitrate = "docker exec IperfClient cat /home/iperf/iperf.log | grep -a 'receiver' | tail -n 1 | awk '{print $7}' | sed 's/[A-Za-z]*//g'"
    
    senderJitter = "docker exec IperfClient cat /home/iperf/iperf.log | grep -a 'sender' | tail -n 2 | awk '{print $9}' | sed 's/[A-Za-z]*//g'"
    receiverJitter = "docker exec IperfClient cat /home/iperf/iperf.log | grep -a 'receiver' | tail -n 1 | awk '{print $9}' | sed 's/[A-Za-z]*//g'"
    
    senderLostTotal = "docker exec IperfClient cat /home/iperf/iperf.log | grep -a 'sender' | tail -n 2 | awk '{print $11}' | sed 's/[A-Za-z]*//g'"
    receiverLostTotal = "docker exec IperfClient cat /home/iperf/iperf.log | grep -a 'receiver' | tail -n 1 | awk '{print $11}' | sed 's/[A-Za-z]*//g'"
    
    # รันคำสั่งย่อยเพื่อดึงค่าจาก log
    result1 = subprocess.run(senderInterval, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    result2 = subprocess.run(receiverInterval, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    result3 = subprocess.run(senderTransfer, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    result4 = subprocess.run(receiverTransfer, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    result5 = subprocess.run(senderBitrate, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    result6 = subprocess.run(receiverBitrate, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    result7 = subprocess.run(senderJitter, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    result8 = subprocess.run(receiverJitter, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    result9 = subprocess.run(senderLostTotal, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    result10 = subprocess.run(receiverLostTotal, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # จัดเก็บผลลัพธ์ใน dictionary เพื่อบันทึกลง JSON
    return {
        "senderInterval": result1.stdout.strip(),
        "receiverInterval": result2.stdout.strip(),
        "senderTransfer": result3.stdout.strip(),
        "receiverTransfer": result4.stdout.strip(),
        "senderBitrate": result5.stdout.strip(),
        "receiverBitrate": result6.stdout.strip(),
        "senderJitter": result7.stdout.strip(),
        "receiverJitter": result8.stdout.strip(),
        "senderLostTotal": result9.stdout.strip(),
        "receiverLostTotal": result10.stdout.strip()
    }
    
# ฟังก์ชัน getcpu ใช้ mpstat เพื่อเก็บค่า CPU usage
def getcpu(time_test,):
    command = f"docker exec VPNserver bash -c 'for i in {{1..{time_test}}}; do mpstat -P ALL 1 1 | grep \"all\" | awk \"NR==1 {{print \\$12}}\"; done'"
    
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = result.stdout.decode('utf-8').splitlines()

    # แปลงค่า %idle เป็นค่า CPU ที่ถูกใช้
    cpu_usages = [100 - float(idle) for idle in output]

    # คำนวณค่าเฉลี่ยของ CPU ที่ถูกใช้
    avg_cpu_usage = sum(cpu_usages) / len(cpu_usages)

    # คืนค่าผลลัพธ์ CPU ที่ถูกใช้
    return avg_cpu_usage


# ฟังก์ชัน get_memory_usage เพื่อเก็บค่า RAM usage
def get_memory_usage(time_test,):
    command = f"docker exec VPNserver bash -c 'for i in {{1..{time_test}}}; do free | awk \"/Mem/ {{printf(\\\"%.2f\\\\n\\\", \\$3/\\$2 * 100.0)}}\"; sleep 1; done'"

    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = result.stdout.decode('utf-8').splitlines()

    # แปลงค่าใน output จาก string เป็น float
    ram_usages = [float(x) for x in output]

    # คำนวณค่าเฉลี่ยการใช้ RAM
    avg_ram_usage = sum(ram_usages) / len(ram_usages)

    # คืนค่าผลลัพธ์ RAM ที่ถูกใช้
    return avg_ram_usage


# เรียกใช้ฟังก์ชัน main เมื่อสคริปต์ถูกเรียกใช้โดยตรง
if __name__ == "__main__":
    main()
