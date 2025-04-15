FROM ubuntu:24.04

# Install Fluent Bit from official repository
RUN apt-get update && \ 
    apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    gnupg && \
    mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://packages.fluentbit.io/fluentbit.key | gpg --dearmor -o /etc/apt/keyrings/fluentbit.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/fluentbit.gpg] https://packages.fluentbit.io/ubuntu/jammy jammy main" > /etc/apt/sources.list.d/fluentbit.list && \
    apt-get update && \
    apt-get install -y \
    fluent-bit \
    && \
    rm -rf /var/lib/apt/lists/*

# Copy configuration files
COPY fluent-bit.conf /etc/fluent-bit/fluent-bit.conf
COPY parsers.conf /etc/fluent-bit/parsers.conf

EXPOSE 5170/tcp 2020/tcp

# Use the correct binary path
CMD ["/opt/fluent-bit/bin/fluent-bit", "-c", "/etc/fluent-bit/fluent-bit.conf"]
 
