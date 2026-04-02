FROM alpine:3.18

RUN apk update && \
    apk add --no-cache frr iptables iproute2 bash && \
    rm -rf /var/cache/apk/*

# keep image minimal; entrypoint handled by compose command
