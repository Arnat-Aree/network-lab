FROM alpine:3.18

RUN apk update && \
    apk add --no-cache iproute2 && \
    rm -rf /var/cache/apk/*

# R2 doesn't need iptables in this lab but include iproute2 for routing
