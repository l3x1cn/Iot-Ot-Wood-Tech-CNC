# Przejęty komputer biurowy: zestaw narzędzi do rozpoznania i analizy ruchu w labie.
FROM ubuntu:26.04
# tshark: dekodery Wiresharka w wierszu poleceń, do zrzutów z nagrań (make v0-analiza).
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      iproute2 iputils-ping curl nmap tcpdump tshark mosquitto-clients dsniff python3-scapy python3-pymodbus \
 && rm -rf /var/lib/apt/lists/*
COPY brama.sh /usr/local/bin/brama.sh
ENTRYPOINT ["/usr/local/bin/brama.sh"]
CMD ["sleep", "infinity"]
