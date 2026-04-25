.PHONY: up down logs ps build shell redis-cli

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

ps:
	docker compose ps

build:
	docker compose build --no-cache

shell:
	docker compose exec app sh

redis-cli:
	docker compose exec cache redis-cli
