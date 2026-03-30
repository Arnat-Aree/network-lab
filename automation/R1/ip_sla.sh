#!/bin/sh
# auto-detect default gateway, fallback to known value
INTERNET_GW="172.30.0.254"
CHECK_HOST="172.30.0.254"
STATE="up"

echo "[IP SLA] Started - monitoring $CHECK_HOST every 5s (gw=$INTERNET_GW)"

while true; do
    if ping -c 1 -W 2 $CHECK_HOST > /dev/null 2>&1; then
        if [ "$STATE" = "down" ]; then
            echo "[IP SLA] Internet RESTORED - adding default route back"
            ip route add default via $INTERNET_GW 2>/dev/null || true
            STATE="up"
        fi
    else
        if [ "$STATE" = "up" ]; then
            echo "[IP SLA] Internet FAILED - removing default route"
            ip route del default via $INTERNET_GW 2>/dev/null || true
            STATE="down"
        fi
    fi
    sleep 5
done