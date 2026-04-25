# Docker Compose Cheatsheet

## CLI Commands

```bash
# Start / Stop
docker compose up                     # start (foreground)
docker compose up -d                  # start (detached)
docker compose up --build             # rebuild before start
docker compose up --build SERVICE     # rebuild one service
docker compose down                   # stop + remove containers & networks
docker compose down -v                # also remove named volumes
docker compose down --rmi all         # also remove images
docker compose stop                   # stop without removing
docker compose start                  # start stopped services
docker compose restart                # restart all
docker compose restart SERVICE        # restart one service

# Status
docker compose ps                     # service status
docker compose top                    # processes in containers
docker compose images                 # images used by services

# Logs
docker compose logs                   # all logs
docker compose logs -f                # follow all
docker compose logs -f SERVICE        # follow one service
docker compose logs --tail 50         # last 50 lines

# Exec & Run
docker compose exec SERVICE sh        # shell in running container
docker compose exec SERVICE CMD       # run command
docker compose run --rm SERVICE CMD   # one-off container

# Build
docker compose build                  # build all images
docker compose build SERVICE          # build one service
docker compose build --no-cache       # build without cache
docker compose pull                   # pull latest base images

# Config
docker compose config                 # validate + print merged config
docker compose config --services      # list service names
docker compose config --volumes       # list volume names

# Scaling
docker compose up -d --scale web=3   # run 3 replicas of web

# Cleanup
docker compose rm                     # remove stopped containers
docker compose rm -f                  # force remove
```

## Compose File Anatomy

```yaml
version: "3.8"

services:
  SERVICE_NAME:
    image: IMAGE:TAG               # pre-built image
    build:                         # OR build from Dockerfile
      context: ./dir
      dockerfile: Dockerfile
      args:
        KEY: value
      target: STAGE                # multi-stage build target
    container_name: NAME
    ports:
      - "HOST:CONTAINER"
    environment:
      - KEY=VALUE
    env_file:
      - .env
    volumes:
      - HOST_PATH:CONTAINER_PATH   # bind mount
      - VOLUME_NAME:CONTAINER_PATH # named volume
    networks:
      - NETWORK_NAME
    depends_on:
      OTHER_SERVICE:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    restart: unless-stopped
    command: ["CMD", "ARG"]
    entrypoint: ["/entrypoint.sh"]
    user: "1000:1000"
    working_dir: /app
    profiles: ["debug"]
    deploy:
      resources:
        limits:
          cpus: "0.5"
          memory: 256M

volumes:
  VOLUME_NAME:                     # Docker-managed storage
    external: true                 # use pre-existing volume

networks:
  NETWORK_NAME:
    driver: bridge
    internal: true                 # no external internet
```

## Key Patterns

```bash
# Use .env file — auto-loaded from same directory
# Reference in compose with ${VAR} or ${VAR:-default}

# Override for local dev (auto-merged)
# docker-compose.yml      → base config
# docker-compose.override.yml → dev overrides (gitignored)

# Explicit multi-file merge
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Target a specific project name (avoids name collision)
docker compose -p myproject up -d
```
