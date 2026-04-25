.PHONY: up down logs ps build shell mongo-shell seed clean

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

mongo-shell:
	docker compose exec mongo mongosh \
	  -u $${MONGO_USER} -p $${MONGO_PASSWORD} --authenticationDatabase admin

seed:
	docker compose exec app python seed.py

clean:
	docker compose down -v
