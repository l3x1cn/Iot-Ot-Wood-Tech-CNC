#!/bin/sh
# Router labu: usuwa trasę domyślną Dockera (lab nie wychodzi do prawdziwego internetu),
# ładuje reguły nftables z /etc/router/nftables.nft i czeka na zatrzymanie.
set -e
ip route del default 2>/dev/null || true
nft -f /etc/router/nftables.nft
echo "router: ip_forward=$(cat /proc/sys/net/ipv4/ip_forward)"
ip -br addr
nft list ruleset
trap 'exit 0' TERM INT
while :; do sleep 3600 & wait $!; done
