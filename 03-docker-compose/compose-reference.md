# Docker Compose File Reference

## Top-Level Keys

```yaml
version: "3.8"   # Compose file format version
services:         # container definitions
volumes:          # named volume declarations
networks:         # custom network declarations
configs:          # config objects (Swarm)
secrets:          # secret objects (Swarm)
```

## Service Keys

### image vs build
```yaml
services:
  web:
    image: nginx:alpine          # use a pre-built image

  app:
    build:                       # build from a Dockerfile
      context: ./app             # build context (directory)
      dockerfile: Dockerfile.prod
      args:
        NODE_ENV: production
      target: runner             # build up to this stage (multi-stage)
      cache_from:
        - myapp:cache
```

### ports
```yaml
ports:
  - "8080:80"           # HOST:CONTAINER
  - "127.0.0.1:8080:80" # bind to specific host interface
  - "80"                # random host port → container 80
```

### environment
```yaml
environment:
  - NODE_ENV=production         # list form
  - DB_HOST=db

  # OR map form
  NODE_ENV: production
  DB_HOST: db
  API_KEY: ${API_KEY}           # value from shell or .env file
```

### env_file
```yaml
env_file:
  - .env
  - .env.local
```

### volumes
```yaml
volumes:
  - ./src:/app/src              # bind mount
  - node_modules:/app/node_modules  # named volume (stops host overwriting)
  - /tmp                        # anonymous volume
  - type: bind
    source: ./config
    target: /etc/config
    read_only: true
```

### networks
```yaml
networks:
  - frontend
  - backend
```

### depends_on
```yaml
depends_on:
  db:
    condition: service_healthy    # wait for healthcheck to pass
  cache:
    condition: service_started    # just wait for container to start
```

### healthcheck
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s    # grace period before healthcheck counts
```

### restart
```yaml
restart: "no"            # default
restart: always          # always restart on exit
restart: on-failure      # only on non-zero exit code
restart: unless-stopped  # always, except when manually stopped
```

### resources (limits)
```yaml
deploy:
  resources:
    limits:
      cpus: "0.5"
      memory: 256M
    reservations:
      memory: 128M
```

### command and entrypoint
```yaml
command: ["gunicorn", "--workers", "4", "app:app"]
entrypoint: ["/docker-entrypoint.sh"]
```

### profiles (selective startup)
```yaml
services:
  app:
    image: myapp

  debug:
    image: myapp
    profiles: ["debug"]    # only starts with: docker compose --profile debug up
```
