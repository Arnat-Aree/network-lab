#!/bin/sh
echo 1 > /proc/sys/net/ipv4/ip_forward

# === Detect interface names dynamically (Docker assigns eth* non-deterministically) ===
INET_IF=$(ip -4 -o addr | grep '172\.30\.0\.2/' | awk '{print $2}')
ISP_IF=$(ip -4 -o addr | grep '172\.31\.0\.1/' | awk '{print $2}')
LAN_A_IF=$(ip -4 -o addr | grep '172\.20\.10\.1/' | awk '{print $2}')

echo "Detected interfaces: INET=$INET_IF  ISP=$ISP_IF  LAN_A=$LAN_A_IF"

# start FRR routing daemon (OSPF)
# Update FRR interface descriptions to match actual interface names
sed -i "s/^interface eth0/interface $INET_IF/" /etc/frr/frr.conf
sed -i "s/^interface eth1/interface $ISP_IF/" /etc/frr/frr.conf
sed -i "s/^interface eth2/interface $LAN_A_IF/" /etc/frr/frr.conf
sed -i "s/passive-interface eth2/passive-interface $LAN_A_IF/" /etc/frr/frr.conf
/usr/lib/frr/frrinit.sh start
sleep 2

ip route replace default via 172.30.0.254
ip route replace 172.20.20.0/24 via 172.31.0.2

# ensure container can resolve public DNS while init runs
echo "nameserver 8.8.8.8" > /etc/resolv.conf

# === NAT (SNAT + DNAT) ===
iptables -t nat -F
iptables -t nat -A POSTROUTING -o $INET_IF -j MASQUERADE
iptables -t nat -A POSTROUTING -o $LAN_A_IF -d 172.20.10.10 -p tcp --dport 8000 -j MASQUERADE
iptables -t nat -A PREROUTING -i $INET_IF -p tcp --dport 8000 -j DNAT --to-destination 172.20.10.10:8000

# === Firewall (FORWARD chain) ===
iptables -F FORWARD
iptables -A FORWARD -i $ISP_IF -s 172.20.20.0/24 -d 172.20.10.0/24 -j ACCEPT
iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A FORWARD -i $LAN_A_IF -j ACCEPT
iptables -A FORWARD -i $INET_IF -p tcp --dport 8000 -d 172.20.10.10 -j ACCEPT
iptables -A FORWARD -i $ISP_IF -j DROP

echo "R1 ready"
# start IP SLA monitor in background if present
if [ -x /automation/ip_sla.sh ]; then
	echo "Starting ip_sla monitor..."
	sh /automation/ip_sla.sh &
fi
