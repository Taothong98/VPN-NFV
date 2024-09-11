import subprocess
import threading

# ตัวแปร ip_address ที่อยู่ภายนอกฟังก์ชัน
ip_address = "192.168.100.100"
time_test = "10"
bandwidth = "1Gb"
parallel = "1"
buffer = "8KB"

# ฟังก์ชัน main ที่เรียกใช้ฟังก์ชันอื่นๆ
def main():
    # สร้าง threads สำหรับ iperf และ getcpu
    iperf_thread = threading.Thread(target=iperf)
    getcpu_thread = threading.Thread(target=getcpu)
    getmem_thread = threading.Thread(target=get_memory_usage)
    
    
    
    # เรียกใช้ทั้งสองฟังก์ชันพร้อมกัน
    iperf_thread.start()
    getcpu_thread.start()
    getmem_thread.start()
    
    
    # รอให้ทั้งสองฟังก์ชันเสร็จสิ้นการทำงาน
    iperf_thread.join()
    getcpu_thread.join()
    getmem_thread.join()
    
    


# ฟังก์ชัน iperf ใช้ตัวแปร ip_address จากภายนอก
def iperf():
    # สร้างคำสั่งโดยใช้ f-string
    # docker exec -it IperfClient iperf3 -c 192.168.100.100 -t 100 -b 100
    command = f"docker exec IperfClient iperf3 -c {ip_address} -u -t {time_test} -b {bandwidth} -P {parallel} >> iperf.log"
    command2 = f"docker exec IperfClient iperf3 -c {ip_address} -u -t {time_test} -b {bandwidth} -P {parallel} >> iperf.log"
    command3 = f"docker exec IperfClient iperf3 -c {ip_address} -u -t {time_test} -b {bandwidth} -P {parallel} >> iperf.log"
    
    
    # command = f"docker exec IperfClient iperf3 -c {ip_address} -t {time_test} -b {bandwidth} -P {parallel} > iperf.log"
    
    
    # ใช้ subprocess ในการรันคำสั่ง
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    result2 = subprocess.run(command2, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    result3 = subprocess.run(command3, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    
    
    # ตรวจสอบผลลัพธ์และแสดงผล
    # if result.returncode == 0:
    #     print("Output:\n", result.stdout)
    # else:
    #     print("Error:\n", result.stderr)


def getcpu():
    # ########################### top เพื่อเก็บค่า CPU usage###############################
    # docker exec -it VPNserver top -b -d 1 -n 10 | grep 'CPU:' | grep 'idle' | awk '{print $8}' | sed 's/[%]*//g'
    # command = f"docker exec VPNserver top -b -d 1 -n {time_test} | grep 'CPU:' | grep 'idle' | awk '{{print $8}}' | sed 's/[%]*//g'"
    
    # ########################### mpstat เพื่อเก็บค่า CPU usage###############################
    # mpstat -P ALL 1 1 | grep "all" | awk 'NR==1 {print $12}'
    # command = "docker exec VPNserver mpstat -P ALL 1 1 | grep 'all' | awk 'NR==1 {print $12}'"    
    # command = "docker exec VPNserver bash -c 'for i in {1..10}; do mpstat -P ALL 1 1 | grep \"all\" | awk \"NR==1 {print \$12}\"; done'"    
    command = f"docker exec VPNserver bash -c 'for i in {{1..{time_test}}}; do mpstat -P ALL 1 1 | grep \"all\" | awk \"NR==1 {{print \\$12}}\"; done'"
        
    # command = "docker exec VPNserver top -b -d 1 -n 10 | grep 'CPU:' | grep 'idle' | awk '{print $8}' | sed 's/[%]*//g'"
    # ใช้ subprocess เพื่อรัน command
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # แปลงผลลัพธ์เป็น string และแยกบรรทัด
    output = result.stdout.decode('utf-8').splitlines()
    # print(output)
    # แปลงค่า %idle เป็นค่า CPU ที่ถูกใช้ (100 - %idle)
    cpu_usages = [100 - float(idle) for idle in output]
    print(cpu_usages)
    # คำนวณค่าเฉลี่ยของ CPU ที่ถูกใช้
    avg_cpu_usage = sum(cpu_usages) / len(cpu_usages)
    # return avg_cpu_usage
    print(f"Average CPU usage over {time_test} samples: {avg_cpu_usage:.2f}%")


def get_memory_usage():
    # command = f"docker exec VPNserver bash -c 'for i in {{1..{time_test}}}; do free | awk \"/Mem/ {{printf(\\\"%.2f\\\\n\\\", \\$3/\\$2 * 100.0)}}\"; done'"
    command = f"docker exec VPNserver bash -c 'for i in {{1..{time_test}}}; do free | awk \"/Mem/ {{printf(\\\"%.2f\\\\n\\\", \\$3/\\$2 * 100.0)}}\"; sleep 1; done'"

    # ใช้ subprocess เพื่อรัน command
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # แปลงผลลัพธ์เป็น string และแยกบรรทัด
    output = result.stdout.decode('utf-8').splitlines()
    print(output)
    # แปลงค่าใน output จาก string เป็น float
    ram_usages = [float(x) for x in output]

    # คำนวณค่าเฉลี่ยการใช้ RAM
    avg_ram_usage = sum(ram_usages) / len(ram_usages)

    print(f"Average RAM usage over {time_test} samples: {avg_ram_usage:.2f}%")  

# เรียกใช้ฟังก์ชัน main เมื่อสคริปต์ถูกเรียกใช้โดยตรง
if __name__ == "__main__":
    main()
