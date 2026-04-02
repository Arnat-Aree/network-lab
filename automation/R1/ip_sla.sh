#!/bin/sh
# IP SLA Monitor — R1 WAN Health Check
# Pings the internet gateway every 5 seconds.
# On failure: removes ALL default routes + withdraws OSPF default-information
# On recovery: restores default route + re-enables OSPF default-information

INTERNET_GW="172.30.0.254"
CHECK_HOST="172.30.0.254"
STATE="up"

echo "[IP SLA] Started - monitoring $CHECK_HOST every 5s (gw=$INTERNET_GW)"

while true; do
    if ping -c 1 -W 2 $CHECK_HOST > /dev/null 2>&1; then
        if [ "$STATE" = "down" ]; then
            echo "[IP SLA] Internet RESTORED - adding default route back"
            ip route add default via $INTERNET_GW 2>/dev/null || true
            # re-enable OSPF default route advertisement
            vtysh -c "configure terminal" -c "router ospf" -c "default-information originate always" -c "end" 2>/dev/null || true
            STATE="up"
        fi
    else
        if [ "$STATE" = "up" ]; then
            echo "[IP SLA] Internet FAILED - removing default route"
            # remove ALL default routes (manual + FRR-injected)
            while ip route del default 2>/dev/null; do :; done
            # withdraw OSPF default route so R2 also loses it
            vtysh -c "configure terminal" -c "router ospf" -c "no default-information originate" -c "end" 2>/dev/null || true
            STATE="down"
        fi
    fi
    sleep 5
done