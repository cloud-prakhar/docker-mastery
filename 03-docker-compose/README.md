# 03 — Docker Compose

Docker Compose lets you define and run multi-container applications with a single YAML file.

## How Compose Works Under the Hood

Compose is not a separate container system — it is a thin orchestrator that reads your YAML file and translates it into the same Docker API calls you would make manually.

```
docker-compose.yml
        │
        │  docker compose up
        ▼
  Compose reads YAML
        │
        ├── creates networks  (docker network create …)
        ├── creates volumes   (docker volume create …)
        └── starts services   (docker container run … for each service)
                │
                ▼
        Docker Daemon
        (same daemon that handles docker run)
```

Key implications for beginners:
- Everything Compose does you *could* do with `docker run` flags — Compose just makes it repeatable and readable
- `docker compose down` reverses only what Compose created (containers + networks); volumes survive unless you add `-v`
- Services talk to each other by **service name** because Compose creates a shared network and registers each service name in Docker's embedded DNS

> Related: [Container networking](../05-networking/) explains how that DNS resolution works.  
> Related: [Volumes](../04-volumes/) explains the persistence model referenced by `volumes:` keys.

## Why Compose?

Without Compose, starting a web app + database + cache requires:
```bash
docker network create app-net
docker volume create pgdata
docker run -d --name postgres --network app-net -e POSTGRES_PASSWORD=secret -v pgdata:/var/lib/postgresql/data postgres:16
docker run -d --name redis --network app-net redis:7-alpine
docker run -d --name web --network app-net -p 8080:8080 -e DB_HOST=postgres -e REDIS_HOST=redis myapp
```

With Compose, it's just:
```bash
docker compose up -d
```

## Core Commands

```bash
docker compose up -d              # start all services in background
docker compose up --build         # rebuild images before starting
docker compose down               # stop and remove containers + networks
docker compose down -v            # also remove named volumes
docker compose ps                 # list service containers
docker compose logs -f            # follow all logs
docker compose logs -f web        # follow logs for one service
docker compose exec web sh        # shell in a running service
docker compose run --rm web bash  # one-off container for a service
docker compose build              # build images without starting
docker compose pull               # pull latest base images
docker compose restart web        # restart one service
docker compose top                # processes in all containers
docker compose config             # validate and print merged config
```

## File Structure

```yaml
# docker-compose.yml
services:
  web:           # service name (also the DNS hostname)
    image: nginx:alpine
    ports:
      - "8080:80"

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_PASSWORD: secret
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:          # named volumes declaration
  pgdata:

networks:         # optional: custom networks
  default:
    driver: bridge
```

## Files in This Section

- [basic-compose.yml](./basic-compose.yml) — single-service example
- [multi-service.yml](./multi-service.yml) — web + db + cache
- [compose-reference.md](./compose-reference.md) — full spec walkthrough
- [env-and-override.md](./env-and-override.md) — `.env` files and `docker-compose.override.yml`

## Next

→ [04 — Volumes](../04-volumes/)
