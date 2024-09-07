# !/bin/bash
service iperf3 start
iperf3 -s 


service apache2 start
apache=echo "apache2ctl -D FOREGROUND"
eval $apache 


