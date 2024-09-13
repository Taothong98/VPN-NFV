# WireGuard in Docker

## How to run this image

-   a host with WireGuard support in the kernel is needed
-   a `wg-quick` style config file needs to be mounted at
    `/etc/wireguard/wg0.conf`

### Example command

```
docker run \
    --name wireguard \
    -v "$(pwd)":/etc/wireguard \
    -p 55555:38945/udp \
    --cap-add NET_ADMIN \
    --tty --interactive \
    felixfischer/wireguard:latest
```

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
