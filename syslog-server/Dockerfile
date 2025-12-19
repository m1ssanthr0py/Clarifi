FROM ubuntu:22.04

# Install rsyslog
RUN apt-get update && \
    apt-get install -y rsyslog rsyslog-relp && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create directory for remote logs
RUN mkdir -p /var/log/remote

# Copy rsyslog configuration
COPY rsyslog.conf /etc/rsyslog.conf

# Expose syslog ports (UDP and TCP)
EXPOSE 514/udp 514/tcp 601/tcp

# Start rsyslog in foreground
CMD ["rsyslogd", "-n"]
