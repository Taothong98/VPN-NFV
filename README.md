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
