#!/bin/sh
echo 1 > /proc/sys/net/ipv4/ip_forward

# === Detect interface names dynamically (Docker assigns eth* non-deterministically) ===
ISP_IF=$(ip -4 -o addr | grep '172\.31\.0\.2/' | awk '{print $2}')
LAN_B_IF=$(ip -4 -o addr | grep '172\.20\.20\.1/' | awk '{print $2}')

echo "Detected interfaces: ISP=$ISP_IF  LAN_B=$LAN_B_IF"

# start FRR routing daemon (OSPF)
# Update FRR interface descriptions to match actual interface names
sed -i "s/^interface eth0/interface $ISP_IF/" /etc/frr/frr.conf
sed -i "s/^interface eth1/interface $LAN_B_IF/" /etc/frr/frr.conf
sed -i "s/passive-interface eth1/passive-interface $LAN_B_IF/" /etc/frr/frr.conf
/usr/lib/frr/frrinit.sh start
sleep 2

ip route replace 172.20.10.0/24 via 172.31.0.1

echo "R2 ready"
