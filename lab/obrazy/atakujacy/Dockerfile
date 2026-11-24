# Przejęty komputer biurowy: zestaw narzędzi do rozpoznania i analizy ruchu w labie.
FROM ubuntu:26.04
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      iproute2 iputils-ping curl nmap tcpdump mosquitto-clients dsniff python3-scapy python3-pymodbus \
 && rm -rf /var/lib/apt/lists/*
COPY brama.sh /usr/local/bin/brama.sh
ENTRYPOINT ["/usr/local/bin/brama.sh"]
CMD ["sleep", "infinity"]
