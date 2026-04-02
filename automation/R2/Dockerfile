FROM alpine:3.18

RUN apk update && \
    apk add --no-cache frr iproute2 bash && \
    rm -rf /var/cache/apk/*

# R2 doesn't need iptables in this lab but include iproute2 for routing
