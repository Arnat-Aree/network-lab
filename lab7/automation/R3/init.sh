#!/bin/sh
echo 1 > /proc/sys/net/ipv4/ip_forward

ISP_IF=$(ip -4 -o addr | grep '172\.30\.2\.1/' | awk '{print $2}')
LAN_A_IF=$(ip -4 -o addr | grep '172\.20\.10\.3/' | awk '{print $2}')
DMZ_IF=$(ip -4 -o addr | grep '172\.20\.30\.3/' | awk '{print $2}')

sed -i "s/ISP_IF/$ISP_IF/g" /etc/frr/frr.conf
sed -i "s/LAN_A_IF/$LAN_A_IF/g" /etc/frr/frr.conf
sed -i "s/DMZ_IF/$DMZ_IF/g" /etc/frr/frr.conf

chown frr:frr /etc/frr/frr.conf
/usr/lib/frr/frrinit.sh start
sleep 2

ip route add default via 172.30.2.254
ip addr add 172.20.10.1/24 dev $LAN_A_IF 2>/dev/null || true
ip addr add 172.20.30.1/24 dev $DMZ_IF 2>/dev/null || true

iptables -t nat -A POSTROUTING -o $ISP_IF -j MASQUERADE
iptables -A FORWARD -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i $DMZ_IF -o $LAN_A_IF -j ACCEPT
iptables -A FORWARD -i $LAN_A_IF -j ACCEPT
iptables -A FORWARD -i $DMZ_IF -o $ISP_IF -j ACCEPT
iptables -t nat -A PREROUTING -i $ISP_IF -p tcp --dport 80 -j DNAT --to-destination 172.20.30.10:80
iptables -A FORWARD -i $ISP_IF -o $DMZ_IF -p tcp --dport 80 -d 172.20.30.10 -j ACCEPT
iptables -A FORWARD -j DROP

syslogd -R 172.20.10.100:514 -L

echo "R3 Initialized"
