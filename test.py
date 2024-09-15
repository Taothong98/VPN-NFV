import os
import subprocess

def docker_start():
    # หา path ปัจจุบันที่ไฟล์ Python และ docker-compose.yml อยู่
    current_path = os.getcwd()

    # สร้าง command สำหรับ docker-compose ps โดยระบุ path ของไฟล์ docker-compose.yml
    command = f"docker-compose -f {current_path}/docker-compose.yml ps -a"
    compose_restart = f"docker-compose -f {current_path}/docker-compose.yml restart"
    compose_stop = f"docker-compose -f {current_path}/docker-compose.yml stop"
    compose_rm = f"docker-compose -f {current_path}/docker-compose.yml rm -f"
    compose_up = f"docker-compose -f {current_path}/docker-compose.yml up -d"

    # รัน command ที่สร้างขึ้น
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # run_compose_restart = subprocess.run(compose_restart, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    run_compose_stop = subprocess.run(compose_stop, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    run_compose_rm = subprocess.run(compose_rm, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    run_compose_up = subprocess.run(compose_up, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # print(result.stdout)  # แสดงผลลัพธ์ทาง stdout
    # print(run_compose_restart.stdout)  # แสดงผลลัพธ์ทาง stdout
    print(run_compose_stop.stdout)  # แสดงผลลัพธ์ทาง stdout
    print(run_compose_rm.stdout)  # แสดงผลลัพธ์ทาง stdout
    print(run_compose_up.stdout)  # แสดงผลลัพธ์ทาง stdout
    
    # if run_show_int.stderr:  # ตรวจสอบและแสดงผลลัพธ์ error (ถ้ามี)
    #     print(f"Error: {run_show_int.stderr}")

docker_start()