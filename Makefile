
.PHONY: docker/build docker/up docker/down docker/logs/api docker/logs/ui

docker/build:
	docker compose build

docker/up:
	docker compose up -d

docker/down:
	docker compose down

docker/logs/api:
	docker compose logs -f api

docker/logs/ui:
	docker compose logs -f ui
