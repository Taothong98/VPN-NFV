import subprocess
import re

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
        "IperfClient": {
            "wg0": {"bytes": iperfclient_wg0_bytes, "packets": iperfclient_wg0_packets},
            "eth0": {"bytes": iperfclient_eth0_bytes, "packets": iperfclient_eth0_packets}
        },
        "VPNserver": {
            "eth1": {"bytes": vpnserver_eth1_bytes, "packets": vpnserver_eth1_packets},
            "wg0": {"bytes": vpnserver_wg0_bytes, "packets": vpnserver_wg0_packets},
            "eth0": {"bytes": vpnserver_eth0_bytes, "packets": vpnserver_eth0_packets}
        },
        "IperfServer": {
            "eth0": {"bytes": iperfserver_eth0_bytes, "packets": iperfserver_eth0_packets}
        },
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

# เรียกใช้ฟังก์ชันและแสดงผลลัพธ์
data = collect_data()
print(data)
