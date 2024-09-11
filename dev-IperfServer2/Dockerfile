# FROM jessfraz/wireguard

# ENV WG_QUICK_URL https://git.zx2c4.com/WireGuard/plain/src/tools/wg-quick/linux.bash

# RUN apk add --no-cache bash wget openresolv
# RUN wget -O /bin/wg-quick $WG_QUICK_URL \
#     && chmod +x /bin/wg-quick

# COPY docker-entrypoint.sh /usr/bin/

# VOLUME ["/etc/wireguard"]
# EXPOSE 38945/udp

# ENTRYPOINT ["docker-entrypoint.sh"]
# CMD ["wg-quick", "up", "wg0"]

FROM felixfischer/wireguard:latest
RUN apk update
RUN apk add iproute2 
RUN apk add iperf3
ENV TZ=Asia/Bangkok
# RUN ifconfig wg0 mtu 65536  
# RUN ifconfig eth0 mtu 65536

