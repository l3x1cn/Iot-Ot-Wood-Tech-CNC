# Lab Wood-Tech CNC. Wymaga Dockera z pluginem compose (Debian: docker-ce + docker-compose-plugin).
V0 := docker compose -f lab/v0/compose.yaml
CZAS ?= 60

.PHONY: help v0-up v0-up-atak v0-down v0-status v0-logs v0-mqtt v0-capture

help:
	@echo "make v0-up        lab v0 (siec niebezpieczna): router, chmura MQTT, CNC x2, PLC, serwer, stacja CAD"
	@echo "make v0-up-atak   jak v0-up, plus przejety komputer biurowy (biuro-pc)"
	@echo "make v0-status    kontenery i zuzycie pamieci"
	@echo "make v0-logs      logi JSON symulatorow (Ctrl+C konczy)"
	@echo "make v0-mqtt      podglad wszystkich wiadomosci MQTT w chmurze (Ctrl+C konczy)"
	@echo "make v0-capture   zapis ruchu sieci zakladu do evidence/v0-<data>.pcap (CZAS=$(CZAS) s, wymaga sudo)"
	@echo "make v0-down      zatrzymuje i usuwa kontenery i sieci labu v0"

v0-up:
	$(V0) up -d --build

v0-up-atak:
	$(V0) --profile atak up -d --build

v0-down:
	$(V0) --profile atak down

v0-status:
	$(V0) --profile atak ps
	@docker stats --no-stream --format 'table {{.Name}}\t{{.MemUsage}}\t{{.CPUPerc}}' $$($(V0) --profile atak ps -q)

v0-logs:
	$(V0) logs -f cnc-1 cnc-2 plc-odpylanie cad-stacja

v0-mqtt:
	$(V0) exec chmura-mqtt mosquitto_sub -h localhost -t '#' -v

v0-capture:
	@mkdir -p evidence
	sudo timeout $(CZAS) tcpdump -i wt0-zaklad -w evidence/v0-$$(date +%Y%m%d-%H%M%S).pcap || true
