import os
import subprocess

def docker_start():
    # หา path ปัจจุบันที่ไฟล์ Python และ docker-compose.yml อยู่
    current_path = os.getcwd()

    # สร้าง command สำหรับ docker-compose ps โดยระบุ path ของไฟล์ docker-compose.yml
    command = f"docker-compose -f {current_path}/docker-compose.yml ps -a"
    
    restart_docker = f"docker-compose -f {current_path}/docker-compose.yml restart"
    up_docker = f"docker-compose -f {current_path}/docker-compose.yml up -d"
    
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
            result = subprocess.run(up_docker, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            print("auto docker-compose up")
                        
        else:
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
                print("auto docker-compose restart")
            
    else:
        print("Error executing command:\n", result.stderr)


docker_start()