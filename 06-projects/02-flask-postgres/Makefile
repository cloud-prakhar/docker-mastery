.PHONY: up down logs ps build shell db-shell

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

db-shell:
	docker compose exec db psql -U postgres -d appdb
