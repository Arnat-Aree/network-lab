FROM alpine:latest

# Install rsyslog during build time to avoid slow/flaky runtime apk fetching over GitHub Actions
RUN apk add --no-cache rsyslog

# Replace default route to ensure internet access if needed, though no longer strictly needed for apk
CMD ["/bin/sh", "-c", "ip route replace default via 172.20.10.1 && mkdir -p /var/log/central && rsyslogd -n"]
