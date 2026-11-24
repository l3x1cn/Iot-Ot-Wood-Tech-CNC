FROM ubuntu:26.04
RUN apt-get update \
 && apt-get install -y --no-install-recommends nftables iproute2 tcpdump \
 && rm -rf /var/lib/apt/lists/*
COPY start.sh /usr/local/bin/start.sh
ENTRYPOINT ["/usr/local/bin/start.sh"]
