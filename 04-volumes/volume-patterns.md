# Volume Patterns and Gotchas

## Pattern 1: Database Persistence

```yaml
services:
  postgres:
    image: postgres:16-alpine
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      POSTGRES_PASSWORD: secret

volumes:
  pgdata:
```

`docker compose down` preserves the volume; `docker compose down -v` removes it.

## Pattern 2: Seeding a Database

```yaml
services:
  postgres:
    image: postgres:16-alpine
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./db/seed.sql:/docker-entrypoint-initdb.d/01-seed.sql:ro
```

Files in `/docker-entrypoint-initdb.d/` are executed alphabetically on first init (when the data directory is empty). Prefix with numbers to control order.

## Pattern 3: Dev Live Reload

```yaml
services:
  app:
    build: .
    volumes:
      - .:/app                          # bind mount source
      - /app/node_modules               # anonymous volume shadows node_modules
    ports:
      - "3000:3000"
```

The anonymous volume `/app/node_modules` prevents the host's (possibly missing) `node_modules` from overwriting the container's installed dependencies.

## Pattern 4: Shared Volume Between Services

```yaml
services:
  generator:
    image: myapp-worker
    volumes:
      - shared-data:/output

  consumer:
    image: nginx:alpine
    volumes:
      - shared-data:/usr/share/nginx/html:ro

volumes:
  shared-data:
```

## Pattern 5: Read-Only Filesystem with Writable Exceptions

```yaml
services:
  app:
    image: myapp
    read_only: true                     # root filesystem read-only
    volumes:
      - /tmp                            # writable tmp
      - /var/run                        # writable runtime dir
      - appdata:/data                   # writable data volume
```

## Gotchas

### Volume Precedence
When a named volume and a bind mount overlap, the **named volume wins** for that path. If the image has pre-populated content at that path, the named volume gets a copy on first use — subsequent runs use the persisted volume content.

### Permissions on Linux
Files created inside a container are owned by the container's UID. If the container runs as root (UID 0), bind-mounted files will be root-owned on the host.

Fix: run the container as your host UID:
```bash
docker run -u $(id -u):$(id -g) -v $(pwd):/app myapp
```

### macOS/Windows Performance
Bind mounts on macOS and Windows go through a file-sharing layer, which can be slow for write-heavy workloads. Use named volumes for database data.

For development on macOS, consider using **`:delegated`** or **`:cached`** mount options (legacy) or the newer VirtioFS (Docker Desktop 4.6+) which is significantly faster.

## Inspecting Volume Contents

```bash
# Run a temporary container to browse a volume
docker run --rm -it -v myvolume:/data alpine sh
```
