FROM alpine:3.18
RUN apk update && \
    apk add --no-cache frr iptables iproute2 bash strongswan vim tcpdump keepalived && \
    rm -rf /var/cache/apk/*
