

service apache2 start
docker exec -it client ls /etc/wireguard/
docker exec -it client apt install iproute2 -y


docker exec -it client apt-get install resolvconf

docker exec -it client wg-quick up test-user
docker exec -it client wg-quick down test-user     ----- ยกเลิก VPN 
ip addr show test-user

docker exec -it client iperf3 -c 192.168.100.100




docker stats WG-GUI --no-stream



chmod 600 /etc/wireguard/test-user.conf
