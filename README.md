################################### XanMod Kernel (xanmod.org) #################################


hostnamectl

wget -qO - https://dl.xanmod.org/archive.key | gpg --dearmor -vo /usr/share/keyrings/xanmod-archive-keyring.gpg

echo 'deb [signed-by=/usr/share/keyrings/xanmod-archive-keyring.gpg] http://deb.xanmod.org releases main' | tee /etc/apt/sources.list.d/xanmod-release.list

apt update && apt install linux-xanmod-x64v2

--------------------------------------------------------------------------------------------------
ตรวจสอบการมีอยู่ของไฟล์ cpu.rt_runtime_us ในระบบ

ls /sys/fs/cgroup/cpu.rt_runtime_us
/sys/fs/cgroup/cpu.rt_runtime_us
zcat /proc/config.gz | grep CONFIG_RT_GROUP_SCHED

cat /boot/config-$(uname -r) | grep CONFIG_RT_GROUP_SCHED
# CONFIG_RT_GROUP_SCHED is not set

hostnamectl
cat /proc/version

apt update
apt install git

cd /usr/src/
mkdir /usr/src/linux-6.9.9/build
cd /usr/src/linux-6.9.9

wget https://mirrors.edge.kernel.org/pub/linux/kernel/v6.x/linux-6.8.tar.gz
wget https://mirrors.edge.kernel.org/pub/linux/kernel/v5.x/linux-5.15.tar.

wget https://gitlab.com/xanmod/linux/-/archive/6.6.50-rt42-xanmod1/linux-6.6.50-rt42-xanmod1.tar.gz
wget -4 https://gitlab.com/xanmod/linux/-/archive/6.6.50-rt42-xanmod1/linux-6.6.50-rt42-xanmod1.tar.gz


tar -xzvf linux-6.8.tar.gz
tar -xzvf linux-5.15.tar.gz
tar -xzvf linux-6.6.50-rt42-xanmod1.tar.gz

cd linux-6.8/
cd linux-5.15/
cd linux-6.6.50-rt42-xanmod1/


sudo apt install git build-essential fakeroot libncurses-dev libssl-dev ccache bison flex

make menuconfig

# Go to General setup ─> Control Group Support ─> CPU controller ─> Group scheduling for SCHED_RR/FIFO configuration as shown below: 
0 33 4 3

# Go to General setup ─> Kernel .config support and enable access to .config through /proc/config.gz
0 24 25

make -j20


################################### sudoers #################################
apt install install sudoers

nano ls /etc/sudoers

debian  ALL=(ALL:ALL) ALL

usermod -aG root debian
nano /etc/group

groups debian

#################################### install docker #######################################

apt update

apt install apt-transport-https ca-certificates curl gnupg lsb-release -y 

curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt update

apt install docker-ce docker-ce-cli containerd.io -y

docker --version

systemctl enable docker
systemctl start docker


####################################### Docker-compose #################################

curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

chmod +x /usr/local/bin/docker-compose

docker-compose --version

###################################### install git ####################################

apt install git

git clone https://github.com/Taothong98/VPN-NFV.git

sudo apt install python3

---------------------------- Test cpu ----------------------------------

sudo docker exec -it VPNserver apk add --no-cache stress-ng

sudo docker exec -it VPNserver stress-ng --cpu 1 --timeout 60

docker exec -it IperfServer bash
htop
sudo docker exec -it VPNserver htop

docker exec -it VPNserver stress-ng --cpu 0 --cpu-load 70 --timeout 60


stdocker exec -it VPNserver ress-ng --vm 1 --vm-bytes 128M --timeout 60
docker exec -it VPNserver stress-ng --vm 2 --vm-bytes 2G --timeout 60


sudo docker stats VPNserver

sudo docker-compose restart
sudo docker restart VPNserver 

sudo docker-compose up stop
sudo docker-compose up start
sudo docker-compose up -d
































#########################################################333

iperf3 -c 192.168.100.100

docker exec -it IperfClient apk add iperf3
docker exec -it IperfClient iperf3 -c 192.168.100.100

docker stats VPNserver



  cat /proc/cpuinfo
  
  cat /proc/net/dev



======================================= TC ====================================================
สร้าง
tc qdisc add dev wg0 root handle 1:0 htb default 10
tc class add dev wg0 parent 1:0 classid 1:10 htb rate 500Mbit prio 0
tc filter add dev wg0 parent 1:0 prio 0 protocol ip handle 10 fw flowid 1:10

แสดง
tc class show dev wg0

เปลี่ยนแปลงค่า
tc class change dev wg0 classid 1:10 htb rate 30Mbit

ลบ
tc class del dev wg0 classid 1:10

--------------------------------------- TC docker --------------------------------------------
docker exec VPNserver tc class show dev wg0

docker exec VPNserver tc qdisc add dev wg0 root handle 1:0 htb default 10
docker exec VPNserver tc class add dev wg0 parent 1:0 classid 1:10 htb rate 500Mbit prio 0
docker exec VPNserver tc filter add dev wg0 parent 1:0 prio 0 protocol ip handle 10 fw flowid 1:10





####################### Configure the real-time scheduler ###########################



  ขั้นตอนการคอมไพล์เคอร์เนลใน Debian****

ติดตั้ง dependencies สำหรับการคอมไพล์เคอร์เนล: ก่อนอื่น คุณต้องติดตั้งแพ็คเกจที่จำเป็น:
sudo apt update
sudo apt install build-essential libncurses-dev bison flex libssl-dev libelf-dev


ดาวน์โหลดซอร์สโค้ดของเคอร์เนล: ดาวน์โหลดซอร์สเคอร์เนลจาก kernel.org หรือติดตั้งผ่านแพ็คเกจของ Debian:
sudo apt install linux-source


แตกไฟล์ซอร์สโค้ดของเคอร์เนล: ซอร์สโค้ดของเคอร์เนลมักจะถูกเก็บไว้ใน /usr/src/:
cd /usr/src
<!-- tar -xjf linux-source-<version>.tar.bz2 -->
sudo tar -xvf linux-source-6.1.tar.xz
tar -xvf patch-6.9.12.xz
<!-- cd linux-source-<version>/ -->
cd linux-source-6.1/

ปรับแต่งการตั้งค่าเคอร์เนล: ใช้คำสั่ง make menuconfig เพื่อตั้งค่าเคอร์เนลและเปิดใช้งาน CONFIG_RT_GROUP_SCHED:
make menuconfig

ไปที่ General Setup > Cgroup Subsystems
เปิดใช้งานตัวเลือก CONFIG_RT_GROUP_SCHED
General Setup 
 [ ] Enable utilization clamping for RT/FAIR tasks 
(20)   Number of supported utilization clamp buckets (NEW) 

------------
คอมไพล์และติดตั้งเคอร์เนล: เริ่มกระบวนการคอมไพล์เคอร์เนล:
sudo make -j$(nproc)
sudo make modules_install
sudo make install

อัปเดต GRUB และบูตเข้าสู่เคอร์เนลใหม่: อัปเดต GRUB เพื่อให้ระบบรู้จักเคอร์เนลใหม่:
sudo update-grub


หลังจากนั้นรีบูตเครื่องเข้าสู่เคอร์เนลใหม่:
sudo reboot

ใช้เคอร์เนล Real-Time ที่เตรียมไว้แล้ว (PREEMPT_RT Patch): คุณสามารถติดตั้งเคอร์เนลที่รองรับการประมวลผลแบบ Real-Time ที่ถูกคอมไพล์ไว้แล้ว เช่นเคอร์เนลที่มีการรวม PREEMPT_RT Patch ซึ่งรองรับ Real-Time Scheduling โดยเฉพาะ

sudo apt update
sudo apt install linux-image-rt-amd64

พิจารณาใช้ Distribution ที่รองรับ Real-Time Scheduling โดยเฉพาะ:
หากคุณต้องการการประมวลผลแบบ Real-Time อย่างชัดเจน การใช้ distribution เช่น Ubuntu Studio หรือ Debian RT ซึ่งมาพร้อมกับเคอร์เนลที่ปรับแต่งสำหรับ Real-Time Processing อาจเป็นทางเลือกที่ดี

#####################################################################################





