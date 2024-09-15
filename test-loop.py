import subprocess

# สร้างอาเรย์ (list) สำหรับเก็บค่า arguments
bandwidth = ["1Mb", "5Mb", "10Mb", "20Mb", "40Mb", "80Mb", "100Mb", "200Mb", "300Mb"]
link_capacity = ["1Mbit", "5Mbit", "10Mbit", "20Mbit", "40Mbit", "80Mbit", "100Mbit", "200Mbit", "300Mbit"]
# parallel = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
parallel = ["1"]
cpu = ["0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9", "1"]
ram = ["64MiB", "128MiB", "256MiB", "512MiB", "1024MiB", "2048MiB",]

def main():
    add_array()  # เพิ่มค่าเข้าสู่ array
    loop()  # ทำการ loop

def add_array():
    global bandwidth, link_capacity  # ใช้ global เพื่อเข้าถึงตัวแปร array ด้านบน
    
    # เพิ่มค่าลงใน list bandwidth, link_capacity ทีละ 50 จาก 250 ถึง 400
    for i in range(250, 1051, 50):
        bandwidth.append(f"{i}Mb")
        link_capacity.append(f"{i}Mbit")

    print("Added new values to the arrays.")
    
    # แสดงผลลัพธ์ของ arrays ทั้งหมด
    print("Current bandwidth array:", bandwidth)
    print("Current link_capacity array:", link_capacity)
    
    # แสดงจำนวนค่าที่มีใน arrays แต่ละตัว
    print(f"Total number of bandwidth values: {len(bandwidth)}")
    print(f"Total number of link_capacity values: {len(link_capacity)}")    

def loop():
    # รันทั้งหมด 4 ครั้ง
    for run_count in range(4):
        print(f"Run number: {run_count + 1}")

        # ใช้ loop ซ้อนกันเพื่อวนผ่านทุกค่าในอาเรย์
        for cpu_index, cpu_value in enumerate(cpu):    
            for link_capacity_value in link_capacity:    
                for bandwidth_value in bandwidth:
                    
                    print(f"Processing arguments: bandwidth={bandwidth_value}, link_capacity={link_capacity_value}, cpu={cpu_value}")
                    
                    # คำสั่งที่ใช้รัน script
                    command = f"python3 test-performance.py -b {bandwidth_value} -l {link_capacity_value} -cpu {cpu_value}"
                    
                    # รันคำสั่ง
                    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                    # ตรวจสอบผลลัพธ์ที่ได้จากการรันคำสั่ง
                    output = result.stdout.decode()

                    if result.returncode == 0:
                        print(f"Success: {output}")

                        # ตรวจสอบว่ามีข้อความที่ต้องการในผลลัพธ์หรือไม่
                        if "Appended results to output_cpu_100.json when CPU is 100" in output:
                            print("CPU reached 100 and results appended. Changing CPU value in the array.")

                            # เปลี่ยนค่า cpu ในอาเรย์หลังจากพบข้อความ
                            cpu[cpu_index] = cpu_value * 2  # ตัวอย่างการเปลี่ยนค่า cpu (เช่น คูณด้วย 2)

                            # แจ้งเตือนว่าค่า cpu ถูกเปลี่ยนแปลง
                            print(f"CPU value at index {cpu_index} changed to {cpu[cpu_index]}")

                    else:
                        print(f"Error: {result.stderr.decode()}")
# def loop():
#     # รันทั้งหมด 4 ครั้ง
#     for run_count in range(4):
#         print(f"Run number: {run_count + 1}")

#         # ใช้ loop ซ้อนกันเพื่อวนผ่านทุกค่าในอาเรย์
#         for cpu_value in cpu:    
#             for link_capacity_value in link_capacity:    
#                 for bandwidth_value in bandwidth:
                    
#                     print(f"Processing arguments: bandwidth={bandwidth_value}, link_capacity={link_capacity_value}, parallel={cpu_value}")
                    
#                     # คำสั่งที่ใช้รัน script
#                     command = f"python3 test-performance.py -b {bandwidth_value} -l {link_capacity_value} -p {cpu_value}"
                    
#                     # รันคำสั่ง
#                     result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

#                     # ตรวจสอบผลลัพธ์ที่ได้จากการรันคำสั่ง
#                     if result.returncode == 0:
#                         print(f"Success: {result.stdout.decode()}")
#                     else:
#                         print(f"Error: {result.stderr.decode()}")

if __name__ == "__main__":
    main()
