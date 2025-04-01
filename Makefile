include api/Makefile ui/Makefile

.PHONY: watch logs/api logs/ui

watch:
	docker compose watch

logs/api:
	docker compose logs -f api

logs/ui:
	docker compose logs -f ui