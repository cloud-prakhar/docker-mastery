# 07 — Docker Troubleshooting

A practical reference for errors beginners encounter most. Each entry shows the exact error message, why it happens, and how to fix it.

---

## Quick Diagnostic Checklist

Before diving into specifics, run these four commands — they answer 80% of questions:

```bash
docker info                        # is the daemon running? any resource warnings?
docker ps -a                       # what state are all containers in?
docker logs <container-name>       # what did the container say before dying?
docker inspect <container-name>    # full config, mounts, network, exit code
```

---

## 1. Daemon & Installation Errors

### "Cannot connect to the Docker daemon"

```
Cannot connect to the Docker daemon at unix:///var/run/docker.sock.
Is the docker daemon running?
```

**Why it happens:** The Docker daemon is stopped, or you're not in the `docker` group.

```
Your shell
    │
    ▼
/var/run/docker.sock  ←── daemon writes this socket file
    │
    ▼
Docker daemon (dockerd)   ← NOT running → socket missing → error
```

**Fix:**

```bash
# Linux — start the daemon
sudo systemctl start docker
sudo systemctl enable docker   # start on boot

# Check if you need sudo (if so, add yourself to the group)
groups $USER | grep docker
sudo usermod -aG docker $USER
newgrp docker                  # apply without logout

# macOS / Windows — just open Docker Desktop
```

---

### "Permission denied" on Docker socket

```
Got permission denied while trying to connect to the Docker daemon socket
at unix:///var/run/docker.sock: Post ... permission denied
```

**Why it happens:** Your user isn't in the `docker` group.

**Fix:**
```bash
sudo usermod -aG docker $USER
newgrp docker
# Then re-open your terminal and retry
```

---

## 2. Image Errors

### "pull access denied" / "repository does not exist"

```
Error response from daemon: pull access denied for myapp, repository does not
exist or may require 'docker login'
```

**Why it happens:** The image name is wrong, the tag doesn't exist, or the registry needs authentication.

**Fix:**
```bash
# Check the exact name / tag on Docker Hub first
docker search nginx                         # find official name
docker pull nginx:1.25-alpine               # use exact tag

# For private registries
docker login registry.example.com
docker pull registry.example.com/myapp:1.0
```

---

### Docker Hub rate limit hit

```
toomanyrequests: You have reached your pull rate limit.
```

**Why it happens:** Docker Hub limits unauthenticated pulls to 100/6h per IP. See [docker-hub-and-registries.md](../01-basics/docker-hub-and-registries.md#rate-limits).

**Fix:**
```bash
docker login                   # free account → 200 pulls/6h
# Or use a mirror in /etc/docker/daemon.json:
# { "registry-mirrors": ["https://mirror.gcr.io"] }
```

---

### "No space left on device" during pull or build

```
write /var/lib/docker/...: no space left on device
```

**Why it happens:** Docker's image/layer cache has filled the disk.

**Fix:**
```bash
docker system df               # see what's using space
docker system prune            # remove stopped containers, dangling images, unused networks
docker system prune -a         # also remove images with no running container (aggressive)
docker volume prune            # remove volumes not attached to any container
```

---

### Build fails: "COPY failed: file not found"

```
COPY failed: file not found in build context or excluded by .dockerignore: stat app.py: file not found
```

**Why it happens:** The file path in `COPY` is relative to the build context (the directory you pass to `docker build`), not your current shell position.

```
docker build -t myapp .
                      ^
              build context = current directory
              COPY app.py .  → looks for ./app.py inside THIS directory
```

**Fix:**
```bash
ls app.py          # confirm it exists in the directory you're running docker build from
# If running from the wrong directory:
docker build -t myapp -f path/to/Dockerfile ./path/to/context
```

---

### Build fails: network error during `RUN apt-get install`

```
Err:1 http://deb.debian.org/debian bookworm InRelease
  Temporary failure resolving 'deb.debian.org'
```

**Why it happens:** The build container can't reach the internet — usually a DNS or proxy issue.

**Fix (Linux):**
```bash
# Check Docker daemon DNS config
cat /etc/docker/daemon.json
# Add Google DNS if missing:
# { "dns": ["8.8.8.8", "8.8.4.4"] }
sudo systemctl restart docker
```

---

## 3. Container Start / Crash Errors

### Container starts then immediately exits

```bash
docker run myapp
docker ps -a
# STATUS: Exited (1) 2 seconds ago
```

**Why it happens:** The container's main process crashed or finished. A container lives only as long as its PID 1.

**Debugging flow:**
```
docker run myapp  →  exits immediately
        │
        ▼
docker logs <container-id>     ← read the actual error message
        │
        ▼
docker run -it myapp sh        ← launch shell instead of the app
                               ← explore the filesystem / run the app manually
```

**Common root causes and fixes:**

| Exit code | Meaning | Common cause |
|---|---|---|
| `0` | Success | CMD finished normally (e.g., one-shot script) |
| `1` | Application error | Uncaught exception, missing file, bad config |
| `2` | Misuse of shell | Bad command syntax |
| `126` | Permission denied | File not executable |
| `127` | Command not found | Typo in CMD / binary not installed |
| `137` | OOM kill (128+9) | Container hit memory limit |
| `139` | Segfault (128+11) | Rare — bad binary or kernel bug |

---

### "port is already allocated"

```
Error response from daemon: driver failed programming external connectivity:
Bind for 0.0.0.0:8080 failed: port is already allocated
```

**Why it happens:** Something on your host is already using that port.

**Fix:**
```bash
# Find what's using the port
sudo ss -tlnp | grep 8080      # Linux
sudo lsof -i :8080             # macOS/Linux

# Kill it or pick a different host port
docker run -p 9090:8080 myapp  # map host:9090 → container:8080
```

---

### Container keeps restarting (`Restarting` status)

```bash
docker ps
# STATUS: Restarting (1) 5 seconds ago
```

**Why it happens:** Compose or `--restart=always` is configured, but the container keeps crashing.

**Fix:**
```bash
docker logs <container-name> --tail 50   # read the crash reason
docker stop <container-name>             # stop the restart loop
# Fix the underlying error, then restart
```

---

## 4. Networking Errors

### Containers can't reach each other by name

```
flask_app | requests.exceptions.ConnectionError: 
  HTTPConnectionPool(host='postgres', port=5432): Max retries exceeded
```

**Why it happens:** Either the containers are on different networks, or the service name is wrong.

```
  flask_app ──► "postgres" ──► DNS lookup inside Docker
                                     │
                         Same Compose project? → works
                         Different networks?  → fails
                         Wrong service name?  → fails
```

**Debugging:**
```bash
# Check what network each container is on
docker inspect flask_app | grep -A 20 '"Networks"'
docker inspect postgres  | grep -A 20 '"Networks"'

# Test DNS resolution from inside the container
docker exec -it flask_app ping postgres
docker exec -it flask_app nslookup postgres

# List all networks
docker network ls
docker network inspect <network-name>
```

**Fix:** Make sure both services are on the same network in `docker-compose.yml`:
```yaml
services:
  flask_app:
    networks: [app-net]
  postgres:
    networks: [app-net]

networks:
  app-net:
```

---

### "connection refused" to a service that IS running

**Why it happens:** The container is up, but the process inside hasn't finished starting yet (especially databases).

```
postgres container starts
    │
    ├── 0s: postgres process launches
    ├── 2s: initialising database files...
    ├── 5s: running init SQL scripts...
    └── 8s: ✓ ready to accept connections

flask_app starts at 1s  ──► tries to connect ──► refused (DB not ready yet)
```

**Fix:** Use a healthcheck + `depends_on` condition in Compose:
```yaml
services:
  postgres:
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $POSTGRES_USER"]
      interval: 5s
      retries: 5

  flask_app:
    depends_on:
      postgres:
        condition: service_healthy
```

See [compose-reference.md](../03-docker-compose/compose-reference.md) for full healthcheck syntax.

---

## 5. Volume & Permission Errors

### "Permission denied" writing to a mounted volume

```
PermissionError: [Errno 13] Permission denied: '/data/output.csv'
```

**Why it happens:** The process inside the container runs as a non-root user, but the bind-mounted host directory is owned by root (or a different UID).

```
Host directory: /home/user/data  (uid=1000)
Container process: runs as uid=0 (root) or uid=1001
                                           ↑
                        UID mismatch → kernel rejects write
```

**Fix options:**

```bash
# Option 1: change host directory ownership to match container UID
sudo chown -R 1000:1000 ./data

# Option 2: run the container as your host UID
docker run -u $(id -u):$(id -g) myapp

# Option 3 (Compose):
# user: "${UID}:${GID}"   in the service definition
```

---

### Named volume has stale/wrong data

**Why it happens:** Volume data persists across `docker compose down`. Old schema or config from a previous run is still there.

**Fix:**
```bash
docker compose down -v           # remove containers AND volumes
docker volume ls                 # list all volumes
docker volume rm <volume-name>   # remove a specific volume
```

> Warning: this deletes your data. Back up first if needed.

---

### Volume shows empty inside container

**Why it happens:** The image has files at the same path — on first mount, a **named volume** is pre-populated from the image, but a **bind mount** always shows the host directory (even if empty).

```
Named volume (first run):  image files → copied into volume ✓
Bind mount:                host dir   → always shown as-is
                           if host dir is empty → container sees empty
```

**Fix:** If using a bind mount, make sure the host directory has the files you expect:
```bash
ls ./html/         # should have your content
```

---

## 6. Docker Compose Errors

### "service ... has neither an image nor a build context"

```
service "app" has neither an image nor a build context specified
```

**Why it happens:** The service in `docker-compose.yml` is missing both `image:` and `build:` keys.

**Fix:** Add one:
```yaml
services:
  app:
    image: nginx:alpine      # use a pre-built image
    # OR
    build: .                 # build from Dockerfile in current directory
```

---

### Environment variable is empty inside the container

**Why it happens:** `.env` file not found, key not defined, or variable not passed through to the service.

**Debugging:**
```bash
docker compose config          # shows the resolved Compose file with all vars substituted
docker exec -it <container> env | grep MY_VAR   # check what's actually set
```

**Fix:** Make sure `.env` exists (copy from `.env.example`) and the variable is referenced in `docker-compose.yml`:
```yaml
environment:
  - MY_VAR=${MY_VAR}   # explicit pass-through
```

See [env-and-override.md](../03-docker-compose/env-and-override.md) for full env handling.

---

### `docker compose up` fails silently — one service never starts

**Debugging:**
```bash
docker compose up                        # don't use -d at first — see live output
docker compose logs <service-name>       # check one service
docker compose ps                        # see state of each service
```

---

## 7. Docker Desktop (macOS / Windows WSL2) Specifics

### Docker Desktop is slow or consuming too much memory

Docker Desktop runs a Linux VM. By default it grabs up to half your RAM.

**Fix (WSL2 on Windows):** Create or edit `%USERPROFILE%\.wslconfig`:
```ini
[wsl2]
memory=4GB
processors=2
```

Then restart WSL: `wsl --shutdown`

**Fix (macOS):** Docker Desktop → Settings → Resources → limit CPU/Memory.

---

### Bind mount path not found on macOS

```
Error response from daemon: Mounts denied: The path /Users/... is not shared
```

**Fix:** Docker Desktop → Settings → Resources → File Sharing → add your project directory.

---

### WSL2: Docker commands work but containers can't access internet

**Why it happens:** WSL2 networking quirk — DNS breaks after Windows hibernation.

**Fix:**
```bash
wsl --shutdown           # in PowerShell
# Reopen WSL terminal — Docker Desktop reconnects automatically
```

---

## 8. Useful One-Liners

```bash
# Remove ALL stopped containers
docker container prune

# Remove ALL unused images
docker image prune -a

# See real-time resource usage
docker stats

# Follow logs for a Compose service
docker compose logs -f <service>

# Open a shell in a running container
docker exec -it <container> sh      # Alpine/minimal images
docker exec -it <container> bash    # Debian/Ubuntu images

# Copy a file out of a container
docker cp <container>:/path/to/file ./local-copy

# Inspect environment variables in a running container
docker exec <container> env

# See what ports are exposed
docker port <container>

# Find which container is using a volume
docker ps -a --filter volume=<volume-name>
```

---

## Files in This Section

- [project-errors.md](./project-errors.md) — errors specific to the projects in `06-projects/`

## Related Sections

- [02 — Commands](../02-commands/) — full CLI reference
- [03 — Docker Compose](../03-docker-compose/) — Compose config and env files
- [04 — Volumes](../04-volumes/) — volume types and patterns
- [05 — Networking](../05-networking/) — network drivers, DNS, iptables

## Previous

← [06 — Projects](../06-projects/)
