#!/bin/sh
echo 1 > /proc/sys/net/ipv4/ip_forward

ip route replace default via 172.31.0.1
ip route replace 172.20.10.0/24 via 172.31.0.1

echo "R2 ready"
