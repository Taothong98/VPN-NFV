import subprocess

# สร้างอาเรย์ (list) สำหรับเก็บค่า arguments
bandwidth = ["1Mb", "5Mb", "10Mb", "20Mb", "40Mb", "80Mb", "100Mb", "200Mb", "300Mb"]
link_capacity = ["1Mbit", "5Mbit", "10Mbit", "20Mbit", "40Mbit", "80Mbit", "100Mbit", "200Mbit", "300Mbit"]
# parallel = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
parallel = ["1"]
cpu = ["0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9", "1"]
ram = ["64", "128", "256", "512", "1024", "2048",]

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
        for bandwidth_value in bandwidth:
            for link_capacity_value in link_capacity:
                for parallel_value in parallel:
                    print(f"Processing arguments: bandwidth={bandwidth_value}, link_capacity={link_capacity_value}, parallel={parallel_value}")
                    
                    # คำสั่งที่ใช้รัน script
                    command = f"python3 test-performance.py -b {bandwidth_value} -l {link_capacity_value} -p {parallel_value}"
                    
                    # รันคำสั่ง
                    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                    # ตรวจสอบผลลัพธ์ที่ได้จากการรันคำสั่ง
                    if result.returncode == 0:
                        print(f"Success: {result.stdout.decode()}")
                    else:
                        print(f"Error: {result.stderr.decode()}")

if __name__ == "__main__":
    main()
