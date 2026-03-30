#!/bin/sh
echo 1 > /proc/sys/net/ipv4/ip_forward

ip route replace default via 172.30.0.254
ip route replace 172.20.20.0/24 via 172.31.0.2

# ensure container can resolve public DNS while init runs
echo "nameserver 8.8.8.8" > /etc/resolv.conf

# assume base image contains iptables; skip network install in lab environment
iptables -t nat -F
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 8000 -j DNAT --to-destination 172.20.10.10:8000

iptables -F FORWARD
iptables -A FORWARD -i eth1 -s 172.20.20.0/24 -d 172.20.10.0/24 -j ACCEPT
iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A FORWARD -i eth2 -j ACCEPT
iptables -A FORWARD -i eth0 -p tcp --dport 8000 -d 172.20.10.10 -j ACCEPT
iptables -A FORWARD -i eth1 -j DROP

echo "R1 ready"
# start IP SLA monitor in background if present
if [ -x /automation/ip_sla.sh ]; then
	echo "Starting ip_sla monitor..."
	sh /automation/ip_sla.sh &
fi
