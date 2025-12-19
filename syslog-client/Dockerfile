FROM ubuntu:22.04

# Install necessary packages
RUN apt-get update && \
    apt-get install -y \
    rsyslog \
    netcat-openbsd \
    curl \
    python3 \
    python3-pip \
    inetutils-ping \
    vim \
    less && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create scripts directory
RUN mkdir -p /scripts

# Copy traffic generation scripts
COPY scripts/ /scripts/
RUN chmod +x /scripts/*.sh

# Set working directory
WORKDIR /scripts

# Keep container running
CMD ["tail", "-f", "/dev/null"]
