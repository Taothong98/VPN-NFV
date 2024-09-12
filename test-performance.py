import subprocess
import threading
import json

# =================== input for iperf test =================
ip_address = "192.168.100.100"
time_test = "1"
bandwidth = "1Gb"
parallel = "1"
buffer = "non"

# ====================== link_capacity =================

link_capacity = "800kbps"

# ฟังก์ชัน main ที่เรียกใช้ฟังก์ชันอื่นๆ
def main():
    results = {}

    # ฟังก์ชันที่ทำงานร่วมกับ threads เพื่อเก็บผลลัพธ์
    def run_input():
        results["input"] = input()
            
    def run_iperf():
        results["iperf"] = iperf()

    def run_getcpu():
        results["cpu"] = getcpu()

    def run_getmem():
        results["memory"] = get_memory_usage()

    # สร้าง threads สำหรับ iperf, getcpu, และ get_memory_usage
    
    input_thread = threading.Thread(target=run_input)
    iperf_thread = threading.Thread(target=run_iperf)
    getcpu_thread = threading.Thread(target=run_getcpu)
    getmem_thread = threading.Thread(target=run_getmem)

    # เรียกใช้ทั้งสามฟังก์ชันพร้อมกัน
    input_thread.start()
    iperf_thread.start()
    getcpu_thread.start()
    getmem_thread.start()

    # รอให้ทั้งสามฟังก์ชันเสร็จสิ้นการทำงาน
    input_thread.join()
    iperf_thread.join()
    getcpu_thread.join()
    getmem_thread.join()

    # บันทึกผลลัพธ์ลงไฟล์ JSON
    with open('output.json', 'w') as json_file:
        json.dump(results, json_file, indent=4)

    print("Results saved to output.json")
    
def get_shell_output(command):
    # รันคำสั่ง shell และดึงผลลัพธ์กลับมา
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout.strip()    

def input():

    ip_address = get_shell_output("sed -n '6p' ./test-performance.py | awk -F ' = ' '{print $2}' | sed 's/\"//g'")
    time_test = get_shell_output("sed -n '7p' ./test-performance.py | awk -F ' = ' '{print $2}' | sed 's/\"//g'")
    bandwidth = get_shell_output("sed -n '8p' ./test-performance.py | awk -F ' = ' '{print $2}' | sed 's/\"//g'")
    parallel = get_shell_output("sed -n '9p' ./test-performance.py | awk -F ' = ' '{print $2}' | sed 's/\"//g'")
    buffer = get_shell_output("sed -n '10p' ./test-performance.py | awk -F ' = ' '{print $2}' | sed 's/\"//g'")

    return {
        # "ip_address": ip_address,
        "time_test": time_test,
        "bandwidth": bandwidth,
        "parallel": parallel,
        # "buffer": buffer
    }

def set_link_capacity():
    
    command1 = "docker exec VPNserver tc qdisc add dev eth0 root handle 1:0 htb default 10"
    command2 = "docker exec VPNserver tc class add dev eth0 parent 1:0 classid 1:10 htb rate {link_capacity} prio 0"
    command3 = "docker exec VPNserver iptables -A OUTPUT -t mangle -p udp -j MARK --set-mark 10"
    command4 = "docker exec VPNserver tc filter add dev eth0 parent 1:0 prio 0 protocol ip handle 10 fw flowid 1:10"
    
# ฟังก์ชัน iperf ใช้ตัวแปร ip_address จากภายนอก
def iperf():
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
def getcpu():
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
def get_memory_usage():
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
