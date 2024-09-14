import subprocess
import threading
import json
import os
import argparse
import re
import threading
import time


# ฟังก์ชันสำหรับนับเวลา
def timer_thread(stop_event):
    start_time = time.time()
    while not stop_event.is_set():
        elapsed_time = time.time() - start_time
        print(f"Time elapsed: {elapsed_time:.2f} seconds", end="\r")
        # time.sleep(1)  # อัปเดตทุก ๆ 1 วินาที
        time.sleep(0.01)  # ลดหน่วงเป็น 10 ms
    print(f"\nTotal execution time: {elapsed_time:.2f} seconds")
    
def main():
    
    # สร้าง stop_event เพื่อใช้หยุดการทำงานของ timer_thread
    stop_event = threading.Event()

    # เริ่ม timer_thread ใน background
    timer = threading.Thread(target=timer_thread, args=(stop_event,))
    timer.start()    

    args = parse_args()  # รับค่าจาก command-line arguments

    # ตั้งค่า variables ที่เปลี่ยนแปลงได้
    ip_address = args.ip_address
    time_test = args.time_test
    bandwidth = args.bandwidth
    parallel = args.parallel
    buffer_size = args.buffer
    new_cpu_limit = args.new_cpu_limit
    new_ram_limit = args.new_ram_limit
    link_capacity = args.link_capacity
        
    docker_start()  # ต้องให้ docker_start() ทำงานเสร็จก่อน
    results = {}
    
    if new_cpu_limit:
        print(f"Setting modified cpu to {new_cpu_limit}")
        modify_cpu_limit(new_cpu_limit)
        
    if new_ram_limit:
        print(f"Setting modified ram to {new_ram_limit}")
        modify_ram_limit(new_ram_limit)      
        
    if link_capacity:
        print(f"Setting link capacity to {link_capacity}")
        set_link_capacity(link_capacity)    

    # เพิ่มเฉพาะค่าที่ต้องการบันทึกลงใน JSON
    results["arguments"] = {
        "time_test": time_test,
        "bandwidth": bandwidth,
        "parallel": parallel,
        "cpu_limit": new_cpu_limit,
        "ram_limit": new_ram_limit,
        "link_capacity": link_capacity,
    }

    # ฟังก์ชันที่ทำงานร่วมกับ threads เพื่อเก็บผลลัพธ์
    def run_iperf():
        results["iperf"] = iperf(ip_address, time_test, bandwidth, parallel)

    def run_getcpu():
        results["cpu"] = getcpu(time_test)

    def run_getmem():
        results["memory"] = get_memory_usage(time_test)

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

    # ====================== เรียก collect_data ก่อน ping ==========================
    collect_data_result = collect_data()  # เรียก collect_data และเก็บผลลัพธ์
    results["collect_data"] = collect_data_result  # เพิ่มผลลัพธ์ collect_data ลงใน JSON

    # ====================== เรียกฟังก์ชัน ping() และบันทึกผลลัพธ์ลง JSON ======================
    # results["ping"] = ping(ip_address)

    # บันทึกผลลัพธ์ลงไฟล์ JSON
    with open('output_latest.json', 'w') as json_file:
        json.dump(results, json_file, indent=4)

    print("Results including ping saved to output_latest_with_ping.json")

    # บันทึกผลลัพธ์ลงไฟล์ JSON (เขียนต่อท้ายข้อมูลเก่า)
    append_to_json('output_history.json', results)

    print("Results saved to output_latest.json and output_history.json")   
    
    # ตรวจสอบค่า cpu ถ้า cpu == 100 ให้บันทึกไฟล์ใหม่
    if results.get("cpu") >= 30:
        # ถ้าไฟล์ output_cpu_100.json มีอยู่แล้ว ให้โหลดข้อมูลเก่า
        if os.path.exists('output_cpu_100.json'):
            with open('output_cpu_100.json', 'r') as json_file:
                old_data = json.load(json_file)
        else:
            old_data = []  # ถ้าไม่มีไฟล์ ให้เริ่มจาก list ว่างเปล่า

        # เพิ่มข้อมูลใหม่เข้าไปใน old_data
        old_data.append(results)

        # บันทึกข้อมูลทั้งหมดลงไฟล์ output_cpu_100.json
        with open('output_cpu_100.json', 'w') as json_file:
            json.dump(old_data, json_file, indent=4)
        
        print("Appended results to output_cpu_100.json when CPU is 100")

    # หยุดการทำงานของ timer_thread เมื่อ main ทำงานเสร็จ
    stop_event.set()

    # รอให้ thread หยุดทำงาน
    timer.join()
    
    # หยุดการทำงานของ timer_thread เมื่อ main ทำงานเสร็จ
    stop_event.set()

    # รอให้ thread หยุดทำงาน
    timer.join() 
    
    
    
    
    
    
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
    # parser.add_argument('-lc', '--link_capacity', type=str, default="1024Mbit", help='link_capacity of VPN-Server')
    parser.add_argument('-lc', '--link_capacity', type=str, help='link_capacity of VPN-Server')
    # ====================== resource configguration =================
    parser.add_argument('-cpu', '--new_cpu_limit', type=str,default="1", help='resource configguration of .env')
    parser.add_argument('-ram', '--new_ram_limit', type=str,default="1024M", help='resource configguration of .env')
    
    return parser.parse_args()   
    
def get_shell_output(command):
    # รันคำสั่ง shell และดึงผลลัพธ์กลับมา
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout.strip()    

# ฟังก์ชันสำหรับตรวจสอบและแก้ไข CPU
def modify_cpu_limit(new_cpu_limit):
    file_path = '.env'
    current_path = os.getcwd()  # รับ path ปัจจุบัน
    env_file_path = os.path.join(current_path, file_path)  # ประกอบ path ของไฟล์ .env
    
    # อ่านไฟล์จากเส้นทางที่กำหนด
    with open(env_file_path, 'r') as f:
        lines = f.readlines()
    
    # ตรวจสอบค่า CPU ปัจจุบันในไฟล์
    current_cpu_limit = None
    for line in lines:
        if "CPU_limits" in line:
            current_cpu_limit = line.split('=')[1].strip()  # อ่านค่าเป็น string
    
    # ตรวจสอบว่า CPU ตรงกับค่าที่รับเข้ามาหรือไม่
    if current_cpu_limit == new_cpu_limit:
        print("CPU resource is same, you can test it")
    else:
        # ถ้าไม่ตรง ให้ทำการเปลี่ยนแปลงค่า
        new_lines = []
        for line in lines:
            if "CPU_limits" in line:
                new_lines.append(f"CPU_limits={new_cpu_limit}\n")
            else:
                new_lines.append(line)
        
        # เขียนข้อมูลกลับไปที่ไฟล์
        with open(env_file_path, 'w') as f:
            f.writelines(new_lines)
        
        print("CPU limit updated. Auto change success, Check again..")

        # ตรวจสอบค่าหลังจากการเปลี่ยนแปลง
        modify_cpu_limit(new_cpu_limit)

# ฟังก์ชันสำหรับตรวจสอบและแก้ไข RAM
def modify_ram_limit(new_ram_limit):
    file_path = '.env'
    current_path = os.getcwd()  # รับ path ปัจจุบัน
    env_file_path = os.path.join(current_path, file_path)  # ประกอบ path ของไฟล์ .env
    
    # อ่านไฟล์จากเส้นทางที่กำหนด
    with open(env_file_path, 'r') as f:
        lines = f.readlines()
    
    # ตรวจสอบค่า RAM ปัจจุบันในไฟล์
    current_ram_limit = None
    for line in lines:
        if "RAM_limits" in line:
            current_ram_limit = line.split('=')[1].strip()  # อ่านค่าเป็น string
    
    # ตรวจสอบว่า RAM ตรงกับค่าที่รับเข้ามาหรือไม่
    if current_ram_limit == new_ram_limit:
        print("RAM resource is same, you can test it")
    else:
        # ถ้าไม่ตรง ให้ทำการเปลี่ยนแปลงค่า
        new_lines = []
        for line in lines:
            if "RAM_limits" in line:
                new_lines.append(f"RAM_limits={new_ram_limit}\n")
            else:
                new_lines.append(line)
        
        # เขียนข้อมูลกลับไปที่ไฟล์
        with open(env_file_path, 'w') as f:
            f.writelines(new_lines)
        
        print("RAM limit updated. Auto change success, Check again..")

        # ตรวจสอบค่าหลังจากการเปลี่ยนแปลง
        modify_ram_limit(new_ram_limit)
        
def set_link_capacity(link_capacity):
    try:
        # รันคำสั่งผ่าน subprocess และดึงค่า output
        result = subprocess.run(["docker", "exec", "VPNserver", "tc", "class", "show", "dev", "wg0"], 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        show = result.stdout  # เก็บผลลัพธ์ของคำสั่ง

        # ตรวจสอบว่าค่า show มีข้อมูลหรือไม่
        if not show:
            print("tc can't not set")
        else:
            # ดึงค่าที่อยู่หลังคำว่า 'rate' ออกมา (ในที่นี้คือ 30Mbit)
            show_parts = show.split()
            if 'rate' in show_parts:
                show_rate_index = show_parts.index('rate') + 1  # หา index ที่คำว่า 'rate' แล้วบวก 1 เพื่อเอาค่าหลัง 'rate'
                show_rate = show_parts[show_rate_index]  # ดึงค่าหลัง 'rate' (เช่น 30Mbit)
                
                # เปรียบเทียบกับค่า lc ที่ส่งเข้ามา
                if show_rate != link_capacity:
                    print(f"lc not same, auto change rate to {link_capacity}")
                    # เปลี่ยนค่า rate โดยใช้คำสั่ง docker exec
                    change_result = subprocess.run(
                        ["docker", "exec", "VPNserver", "tc", "class", "change", "dev", "wg0", 
                         "classid", "1:10", "htb", "rate", link_capacity],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                    )

                    # ตรวจสอบผลลัพธ์หลังจากเปลี่ยนค่า
                    if change_result.returncode == 0:
                        print("Auto change success, Check again..")
                        # ตรวจสอบอีกครั้งหลังจากเปลี่ยนค่า
                        set_link_capacity(link_capacity)
                    else:
                        print(f"can't change lc: {change_result.stderr}")
                else:
                    print("lc is same, you can test it ")
            else:
                print("nodata")  # ถ้าไม่มีคำว่า 'rate' ในผลลัพธ์
    except Exception as e:
        print(f"Error lc function: {e}")
        
    
def docker_start():
    # หา path ปัจจุบันที่ไฟล์ Python และ docker-compose.yml อยู่
    current_path = os.getcwd()

    # สร้าง command สำหรับ docker-compose ps โดยระบุ path ของไฟล์ docker-compose.yml
    command = f"docker-compose -f {current_path}/docker-compose.yml ps -a"    
    restart_compose = f"docker-compose -f {current_path}/docker-compose.yml restart"
    restart_VPNserver = f"docker restart VPNserver "
    restart_IperfClient = f"docker restart IperfClient "
    restart_IperfServer = f"docker restart IperfServer "
    
 
    
    
    # รัน command ที่สร้างขึ้น โดยไม่แสดงผลลัพธ์
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    run_restart_compose = subprocess.run(restart_compose, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    run_restart_VPNserver = subprocess.run(restart_VPNserver, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    run_restart_IperfClient = subprocess.run(restart_IperfClient, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    run_restart_IperfServer = subprocess.run(restart_IperfServer, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    
    # ตรวจสอบผลลัพธ์ (ไม่แสดงผลลัพธ์ออกทาง console)
    if result.returncode == 0:
        # แยกบรรทัดข้อมูลจากผลลัพธ์
        lines = result.stdout.splitlines()

        # ตรวจสอบว่ามี service หรือไม่
        if len(lines) <= 2:  # มีเพียง header แต่ไม่มี service
            result = subprocess.run(restart_compose, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
        else:
            # ตรวจสอบแต่ละบรรทัดที่มีข้อมูล service
            all_up = True
            for line in lines[2:]:  # ข้ามสองบรรทัดแรกที่เป็น header
                if "Up" not in line or "Exited" in line:  # ถ้า service ไหนไม่ขึ้นว่า Up หรือขึ้นว่า Exited
                    all_up = False
                    break

            if not all_up:
                # รีสตาร์ท docker services หากมี service ที่ไม่ทำงานปกติ
                subprocess.run(restart_compose, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
    else:
        # เก็บ error ไว้ แต่ไม่แสดงผล
        pass

   
    
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
        # "senderInterval": f"{result1.stdout.strip()} seconds",    # เพิ่มหน่วยเป็น "seconds"
        # "receiverInterval": f"{result2.stdout.strip()} seconds",  # เพิ่มหน่วยเป็น "seconds"
        "senderTransfer": f"{result3.stdout.strip()} MB",          # เพิ่มหน่วยเป็น "MB"
        "receiverTransfer": f"{result4.stdout.strip()} MB",        # เพิ่มหน่วยเป็น "MB"
        "senderBitrate": f"{result5.stdout.strip()} Mbps",         # เพิ่มหน่วยเป็น "Mbps"
        "receiverBitrate": f"{result6.stdout.strip()} Mbps",       # เพิ่มหน่วยเป็น "Mbps"
        "senderJitter": f"{result7.stdout.strip()} ms",            # เพิ่มหน่วยเป็น "ms"
        "receiverJitter": f"{result8.stdout.strip()} ms",          # เพิ่มหน่วยเป็น "ms"
        "senderLostTotal": f"{result9.stdout.strip()} packets",    # เพิ่มหน่วยเป็น "packets"
        "receiverLostTotal": f"{result10.stdout.strip()} packets"  # เพิ่มหน่วยเป็น "packets"
    }
    
    
# ฟังก์ชันสำหรับเขียนข้อมูลต่อท้ายในไฟล์ JSON
def append_to_json(filename, new_data):
    if os.path.exists(filename):
        # ถ้าไฟล์มีอยู่แล้ว ให้อ่านข้อมูลเก่าเข้ามาก่อน
        with open(filename, 'r') as json_file:
            try:
                data = json.load(json_file)
            except json.JSONDecodeError:
                data = []  # ถ้าไฟล์ว่าง ให้เริ่มเป็นลิสต์ว่าง
    else:
        data = []  # ถ้าไฟล์ไม่มีอยู่ ให้เริ่มเป็นลิสต์ว่าง

    # เพิ่มข้อมูลใหม่ลงในลิสต์
    data.append(new_data)

    # เขียนข้อมูลใหม่กลับลงไฟล์
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)    
    
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


def ping(ip_address):
    command = f"docker exec IperfClient ping {ip_address} -c 5"

    # รันคำสั่ง ping
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # แปลงผลลัพธ์เป็น string
    output = result.stdout.decode('utf-8')

    # ใช้ regular expression เพื่อดึงค่า max round-trip time
    match = re.search(r"min/avg/max = (\d+\.\d+)/(\d+\.\d+)/(\d+\.\d+)", output)

    if match:
        min_val, avg_val, max_val = match.groups()
        # print(f"Max round-trip time: {max_val} ms")
        # return {"min": min_val, "avg": avg_val, "max": max_val}
        return {"max": max_val}
    
    else:
        print("ไม่พบข้อมูล round-trip min/avg/max")
        return {"error": "ไม่พบข้อมูล ping"}

# =========================================================================================

def run_docker_command(container_name):
    # รันคำสั่ง docker exec เพื่อดึงข้อมูลจาก /proc/net/dev ของ container นั้น ๆ
    command = f"docker exec {container_name} cat /proc/net/dev"
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, text=True)
    return result.stdout

def parse_net_dev_output(output, interface, direction):
    # ใช้ regex ในการจับข้อมูล bytes และ packets
    regex_pattern = fr"{interface}:\s+(\d+)\s+(\d+)" if direction == "receive" else fr"{interface}:\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+(\d+)\s+(\d+)"
    match = re.search(regex_pattern, output)
    if match:
        bytes_val, packets_val = int(match.group(1)), int(match.group(2))
        return bytes_val, packets_val
    return 0, 0

def collect_data():
    # รันคำสั่งจากแต่ละ container
    iperfclient_output = run_docker_command('IperfClient')
    vpnserver_output = run_docker_command('VPNserver')
    iperfserver_output = run_docker_command('IperfServer')

    # ดึงข้อมูลที่ต้องการจาก output โดยใช้ function parse_net_dev_output
    iperfclient_wg0_bytes, iperfclient_wg0_packets = parse_net_dev_output(iperfclient_output, "wg0", "transmit")
    iperfclient_eth0_bytes, iperfclient_eth0_packets = parse_net_dev_output(iperfclient_output, "eth0", "transmit")

    vpnserver_eth1_bytes, vpnserver_eth1_packets = parse_net_dev_output(vpnserver_output, "eth1", "receive")
    vpnserver_wg0_bytes, vpnserver_wg0_packets = parse_net_dev_output(vpnserver_output, "wg0", "receive")
    vpnserver_eth0_bytes, vpnserver_eth0_packets = parse_net_dev_output(vpnserver_output, "eth0", "transmit")

    iperfserver_eth0_bytes, iperfserver_eth0_packets = parse_net_dev_output(iperfserver_output, "eth0", "receive")

    # คำนวณค่าต่าง ๆ
    encapsulation_size_bytes = iperfclient_eth0_bytes - iperfclient_wg0_bytes
    encapsulation_size_packets = iperfclient_eth0_packets - iperfclient_wg0_packets

    data_loss_between_containers_bytes = iperfclient_eth0_bytes - vpnserver_eth1_bytes
    data_loss_between_containers_packets = iperfclient_eth0_packets - vpnserver_eth1_packets

    post_decapsulation_loss_bytes = iperfclient_wg0_bytes - vpnserver_wg0_bytes
    post_decapsulation_loss_packets = iperfclient_wg0_packets - vpnserver_wg0_packets

    # สร้าง dictionary เพื่อเก็บผลลัพธ์
    results = {
        # "IperfClient": {
        #     "wg0": {"bytes": iperfclient_wg0_bytes, "packets": iperfclient_wg0_packets},
        #     "eth0": {"bytes": iperfclient_eth0_bytes, "packets": iperfclient_eth0_packets}
        # },
        # "VPNserver": {
        #     "eth1": {"bytes": vpnserver_eth1_bytes, "packets": vpnserver_eth1_packets},
        #     "wg0": {"bytes": vpnserver_wg0_bytes, "packets": vpnserver_wg0_packets},
        #     "eth0": {"bytes": vpnserver_eth0_bytes, "packets": vpnserver_eth0_packets}
        # },
        # "IperfServer": {
        #     "eth0": {"bytes": iperfserver_eth0_bytes, "packets": iperfserver_eth0_packets}
        # },
        "Calculations": {
            "Encapsulation Size": {
                "bytes": encapsulation_size_bytes,
                "packets": encapsulation_size_packets
            },
            "Data Loss Between Containers": {
                "bytes": data_loss_between_containers_bytes,
                "packets": data_loss_between_containers_packets
            },
            "Post Decapsulation Loss": {
                "bytes": post_decapsulation_loss_bytes,
                "packets": post_decapsulation_loss_packets
            }
        }
    }

    return results

# =========================================================================================

# เรียกใช้ฟังก์ชัน main เมื่อสคริปต์ถูกเรียกใช้โดยตรง
if __name__ == "__main__":
    main()
