FROM alpine:3.18

RUN apk update && \
    apk add --no-cache iptables iproute2 && \
    rm -rf /var/cache/apk/*

# keep image minimal; entrypoint handled by compose command
