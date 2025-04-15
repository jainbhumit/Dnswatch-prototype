FROM ubuntu:24.04

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY pdns.list /etc/apt/sources.list.d/pdns.list
COPY rec-50 /etc/apt/preferences.d/rec-50
RUN install -d /etc/apt/keyrings && \
    curl -fsSL https://repo.powerdns.com/FD380FBB-pub.asc | tee /etc/apt/keyrings/rec-50-pub.asc

RUN apt-get update && \
    apt-get install -y \
    pdns-recursor \
    lua-socket && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/run/pdns-recursor && chown pdns:pdns /var/run/pdns-recursor

COPY recursor.conf /etc/powerdns/recursor.conf
COPY custom.lua /etc/powerdns/custom.lua

EXPOSE 5353/udp 5353/tcp

CMD ["/usr/sbin/pdns_recursor", "--daemon=no", "--loglevel=9"]
