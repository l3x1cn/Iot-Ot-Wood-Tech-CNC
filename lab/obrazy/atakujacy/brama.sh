#!/bin/sh
# Ustawia trasę domyślną przez router labu (zamiast bramy Dockera), potem uruchamia polecenie.
set -e
if [ -n "$BRAMA" ]; then
  ip route replace default via "$BRAMA"
fi
exec "$@"
