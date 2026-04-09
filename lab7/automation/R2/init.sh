#!/bin/sh
echo 1 > /proc/sys/net/ipv4/ip_forward

ISP_IF=$(ip -4 -o addr | grep '172\.30\.1\.2/' | awk '{print $2}')
LAN_B_IF=$(ip -4 -o addr | grep '172\.20\.20\.1/' | awk '{print $2}')

cp -a /etc/frr_template/. /etc/frr/

sed -i "s/ISP_IF/$ISP_IF/g" /etc/frr/frr.conf
sed -i "s/LAN_B_IF/$LAN_B_IF/g" /etc/frr/frr.conf

chown frr:frr /etc/frr/frr.conf
/usr/lib/frr/frrinit.sh start
sleep 2

ip route add default via 172.30.1.254

iptables -t nat -A POSTROUTING -o $ISP_IF -j MASQUERADE

cp /automation/ipsec.conf /etc/ipsec.conf
cp /automation/ipsec.secrets /etc/ipsec.secrets
chmod 600 /etc/ipsec.secrets
ipsec start

syslogd -R 172.20.10.100:514 -L

echo "R2 Initialized"
