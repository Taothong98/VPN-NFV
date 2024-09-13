import subprocess
import threading
import json
import os
import argparse
import re



# =================== input for iperf test =================
# ip_address = "192.168.100.100"
# time_test = "1"
# bandwidth = "1Gb"
# parallel = "1"
# buffer = "non"

# ====================== link_capacity =================

# link_capacity = "800kbps"

# ฟังก์ชัน main ที่เรียกใช้ฟังก์ชันอื่นๆ
def main():

    args = parse_args()       # รับค่าจาก command-line arguments

    # ตั้งค่า variables ที่เปลี่ยนแปลงได้
    ip_address = args.ip_address
    time_test = args.time_test
    bandwidth = args.bandwidth
    parallel = args.parallel
    buffer_size = args.buffer
    link_capacity = args.link_capacity
        
    docker_start()  # ต้องให้ docker_start() ทำงานเสร็จก่อน
    results = {}
    
    if link_capacity:
        print(f"Setting link capacity to {link_capacity}")
        set_link_capacity(link_capacity)    
    
    # เพิ่มเฉพาะค่าที่ต้องการบันทึกลงใน JSON
    results["arguments"] = {
        # "ip_address": ip_address,
        "time_test": time_test,
        "bandwidth": bandwidth,
        "parallel": parallel,  # ค่านี้ไม่ต้องการบันทึกไว้ใน JSON
        # "buffer_size": buffer_size,  # ค่านี้ไม่ต้องการบันทึกไว้ใน JSON
        
        "link_capacity": link_capacity,  # ค่านี้ไม่ต้องการบันทึกไว้ใน JSON
        
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

    # บันทึกผลลัพธ์ลงไฟล์ JSON (ไฟล์แรก)
    # with open('output_latest.json', 'w') as json_file:
    #     json.dump(results, json_file, indent=4)

    # # บันทึกผลลัพธ์ลงไฟล์ JSON (ไฟล์ที่สอง - เขียนต่อท้ายข้อมูลเก่า)
    # append_to_json('output_history.json', results)

    # print("Results saved to output_latest.json and output_history.json")
    
 
    #================ เรียกฟังก์ชัน ping() และบันทึกผลลัพธ์ลง JSON ======================
    results["ping"] = ping(ip_address)

    # บันทึกผลลัพธ์รวมถึง ping ลงใน JSON อีกครั้ง
    with open('output_latest.json', 'w') as json_file:
        json.dump(results, json_file, indent=4)

    print("Results including ping saved to output_latest_with_ping.json")
    
    append_to_json('output_history.json', results)

    print("Results saved to output_latest.json and output_history.json")    
       
    
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
    
    return parser.parse_args()   
    
def get_shell_output(command):
    # รันคำสั่ง shell และดึงผลลัพธ์กลับมา
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout.strip()    


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
    
    restart_docker = f"docker-compose -f {current_path}/docker-compose.yml restart"
    
    # รัน command ที่สร้างขึ้น
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # ตรวจสอบผลลัพธ์
    if result.returncode == 0:
        print("Command executed successfully:\n", result.stdout)

        # แยกบรรทัดข้อมูลจากผลลัพธ์
        lines = result.stdout.splitlines()

        # ตรวจสอบว่ามี service หรือไม่
        if len(lines) <= 2:  # มีเพียง header แต่ไม่มี service
            print("Not have service in compose")
            result = subprocess.run(restart_docker, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
        else:
            # ตรวจสอบแต่ละบรรทัดที่มีข้อมูล service
            all_up = True
            for line in lines[2:]:  # ข้ามสองบรรทัดแรกที่เป็น header
                if "Up" not in line or "Exited" in line:  # ถ้า service ไหนไม่ขึ้นว่า Up หรือขึ้นว่า Exited
                    all_up = False
                    break

            if all_up:
                print("All services are up.")
            else:
                print("Some services are not running normally!")
                result = subprocess.run(restart_docker, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                print("Services restarted.")
            
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
        print(f"Max round-trip time: {max_val} ms")
        # return {"min": min_val, "avg": avg_val, "max": max_val}
        return {"max": max_val}
    
    else:
        print("ไม่พบข้อมูล round-trip min/avg/max")
        return {"error": "ไม่พบข้อมูล ping"}


# เรียกใช้ฟังก์ชัน main เมื่อสคริปต์ถูกเรียกใช้โดยตรง
if __name__ == "__main__":
    main()
