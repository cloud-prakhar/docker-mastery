# Environment Variables and Overrides

## .env File

Docker Compose automatically loads a `.env` file from the same directory:

```bash
# .env
POSTGRES_PASSWORD=secret
APP_PORT=8080
IMAGE_TAG=1.2.3
```

Reference values in `docker-compose.yml` with `${VAR}`:

```yaml
services:
  app:
    image: myapp:${IMAGE_TAG}
    ports:
      - "${APP_PORT}:8080"
```

The `.env` file is for **Compose variable substitution** — it's not the same as passing env vars to containers (use `environment:` or `env_file:` for that).

## Compose Override Files

Compose merges multiple files when specified with `-f` or via the automatic override file:

```
docker-compose.yml          ← base config (committed)
docker-compose.override.yml ← local dev overrides (gitignored)
docker-compose.prod.yml     ← production config
```

Compose automatically merges `docker-compose.yml` + `docker-compose.override.yml` when you run `docker compose up`.

### Example: Base + Override Pattern

`docker-compose.yml` (base, production-friendly):
```yaml
services:
  app:
    image: myapp:${IMAGE_TAG:-latest}
    restart: unless-stopped
    environment:
      - NODE_ENV=production
```

`docker-compose.override.yml` (local dev, not committed):
```yaml
services:
  app:
    build: .                     # build locally instead of pulling
    volumes:
      - .:/app                   # live reload source
    environment:
      - NODE_ENV=development
      - DEBUG=1
    ports:
      - "9229:9229"              # debugger port
```

### Explicit Multi-File Merge

```bash
# production
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# staging
docker compose -f docker-compose.yml -f docker-compose.staging.yml up -d
```

## Merge Rules

- **Maps (dict)**: keys are merged; child overrides parent value
- **Lists (sequences)**: child values are **appended** to parent list
- **Scalar (string/number)**: child replaces parent

### Resetting a list

To clear a list set in the base file, use an empty list in the override:

```yaml
# override: clear the ports list
services:
  app:
    ports: []
```

## Variable Precedence (highest to lowest)

1. Shell environment variables
2. `.env` file
3. `environment:` key in compose file
4. Dockerfile `ENV` instruction
