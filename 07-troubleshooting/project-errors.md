# Project-Specific Errors

Common errors learners hit in each of the `06-projects/` stacks, with exact error messages and fixes.

---

## All Projects — `version` attribute is obsolete warning

```
the attribute `version` is obsolete, it will be ignored, please remove it to avoid potential confusion
```

**Why it happens:** Docker Compose v2.20+ (and v5+) dropped support for the top-level `version` key. The `version: "3.8"` line is now a no-op and generates this warning on every `docker compose` command.

> The `version:` line has been removed from all project `docker-compose.yml` files in this repo. If you see this warning in your own Compose files, apply the same fix below.

**Fix:** Remove the `version:` line from the top of the file:
```yaml
# Before (generates warning):
version: "3.8"

services:
  ...

# After (clean):
services:
  ...
```

The `services`, `volumes`, and `networks` keys are still valid — only the version declaration is gone.

---

## Project 01 — Nginx Static Site

### Healthcheck always "unhealthy" even though the site serves correctly

```
NAME                    IMAGE          STATUS
01-nginx-static-web-1   nginx:alpine   Up 2 minutes (unhealthy)
```

**Why it happens:** The default healthcheck uses `wget -qO- http://localhost`, but inside Docker containers `/etc/hosts` maps `localhost` to `::1` (IPv6) first. BusyBox `wget` (used in Alpine) tries IPv6 and fails because `nginx:alpine` only listens on `0.0.0.0:80` (IPv4). The site serves fine on port 8080 from the host, but the internal healthcheck probe always gets "Connection refused".

```
/etc/hosts inside container:
  127.0.0.1  localhost
  ::1        localhost ip6-localhost  ← BusyBox wget picks this first
                                          nginx not listening on IPv6 → refused
```

**Debugging:**
```bash
docker inspect 01-nginx-static-web-1 \
  --format '{{range .State.Health.Log}}{{.Output}}{{end}}'
# Shows: "wget: can't connect to remote host: Connection refused"

# Confirm the root cause:
docker exec 01-nginx-static-web-1 wget -qO- http://localhost   # fails
docker exec 01-nginx-static-web-1 wget -qO- http://127.0.0.1  # works
```

**Fix:** Use the explicit IPv4 address in the healthcheck:
```yaml
healthcheck:
  test: ["CMD", "wget", "-qO-", "http://127.0.0.1"]   # not http://localhost
```

---

### Nginx shows "403 Forbidden"

```
403 Forbidden
nginx/1.25.x
```

**Why it happens:** The bind-mounted `html/` directory exists but either has no `index.html`, or the directory/files have permissions that Nginx (which runs as `nginx` user, uid=101) cannot read.

**Debugging:**
```bash
docker compose logs nginx            # look for "Permission denied" in the log
docker exec -it nginx-container ls -la /usr/share/nginx/html
```

**Fix:**
```bash
# On the host, make files world-readable
chmod -R 755 ./html
chmod 644 ./html/index.html
```

---

### Nginx fails to start: "nginx.conf" syntax error

```
nginx: [emerg] unknown directive "serever" in /etc/nginx/conf.d/default.conf:1
```

**Why it happens:** A typo in the custom `nginx.conf`.

**Fix:**
```bash
# Validate config without starting
docker run --rm -v $(pwd)/nginx.conf:/etc/nginx/conf.d/default.conf:ro nginx nginx -t
#                                                                                    ^ test mode
```

Fix the reported line, then `make up` again.

---

### Port 8080 already in use

```
Error starting userland proxy: listen tcp4 0.0.0.0:8080: bind: address already in use
```

**Fix:**
```bash
sudo ss -tlnp | grep 8080      # find the process
# Change host port in docker-compose.yml:  "9090:80"  instead of "8080:80"
```

---

### Edited HTML file not reflected in browser

**Why it happens:** Browser cache, not Docker.

**Fix:** Hard-refresh: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (macOS).

If still stale, confirm the bind mount path is correct:
```bash
docker inspect nginx-container | grep -A 5 Mounts
```

---

## Project 02 — Flask + PostgreSQL

### Flask exits immediately: "could not connect to server"

```
flask_app | psycopg2.OperationalError: could not connect to server: Connection refused
flask_app |   Is the server running on host "postgres" (172.18.0.2) and accepting
flask_app |   TCP/IP connections on port 5432?
flask_app exited with code 1
```

**Why it happens:** Flask started before Postgres finished initialising. `depends_on` with a healthcheck fixes this, but if the healthcheck is missing or the interval is too short, Flask wins the race.

```
Timeline:
  t=0s   postgres container starts
  t=0.5s flask container starts  ──► tries to connect ──► REFUSED
  t=6s   postgres ready ✓  (too late)
```

**Fix:** Ensure your Compose file has a healthcheck on the `postgres` service AND `condition: service_healthy` on `flask_app`:

```yaml
postgres:
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U $POSTGRES_USER -d $POSTGRES_DB"]
    interval: 5s
    timeout: 5s
    retries: 10
    start_period: 10s

flask_app:
  depends_on:
    postgres:
      condition: service_healthy
```

---

### Flask can't find the database: "FATAL: database does not exist"

```
FATAL:  database "myapp" does not exist
```

**Why it happens:** `POSTGRES_DB` environment variable wasn't set (or the `.env` file wasn't copied).

**Fix:**
```bash
cp .env.example .env
# Edit .env and set POSTGRES_DB=myapp POSTGRES_USER=... POSTGRES_PASSWORD=...
docker compose down -v     # wipe old volume (created without the DB name)
docker compose up
```

---

### "role does not exist" after changing `.env`

```
FATAL:  role "newuser" does not exist
```

**Why it happens:** The Postgres named volume already exists from a previous `docker compose up` with different credentials. Postgres ignores `POSTGRES_USER` on an already-initialised volume.

**Fix:**
```bash
docker compose down -v    # -v removes the named volume
docker compose up         # fresh init with new credentials
```

---

### 500 error from Flask but no traceback in logs

**Fix:**
```bash
docker compose logs flask_app          # Flask prints tracebacks here
docker exec -it flask_app python -c "import psycopg2; print('ok')"   # test the import
```

---

## Project 03 — Node.js + Redis

### Build fails: "npm ci can only install with an existing package-lock.json"

```
npm error code EUSAGE
npm error
npm error The `npm ci` command can only install with an existing package-lock.json or
npm error npm-shrinkwrap.json with lockfileVersion >= 1. Run an install with npm@5 or
npm error later to generate a package-lock.json file, then try again.
```

**Why it happens:** The Dockerfile uses `npm ci` for reproducible, fast installs — but `npm ci` requires a `package-lock.json` to be present in the build context. If the lock file was not committed to the repository (or was `.gitignore`d), the build fails.

```
Dockerfile:
  COPY package*.json ./       ← copies package.json but NOT package-lock.json
  RUN npm ci --only=production  ← requires lock file → error
```

**Fix (preferred — generate and commit the lock file):**
```bash
# On the host (Node.js must be installed)
cd app/
npm install --package-lock-only   # generates lock file without installing node_modules
# Then commit package-lock.json
git add package-lock.json
git commit -m "add package-lock.json for reproducible builds"
```

**Fix (alternative — switch to `npm install` in the Dockerfile):**
```dockerfile
# In Dockerfile, replace:
RUN npm ci --only=production
# with:
RUN npm install --omit=dev
```

> Note: `npm install` re-resolves versions each time and is slower; prefer committing the lock file to keep builds deterministic.

---

### Node exits: "Error: connect ECONNREFUSED 127.0.0.1:6379"

```
node_app | Error: connect ECONNREFUSED 127.0.0.1:6379
```

**Why it happens:** The app is connecting to `127.0.0.1` (localhost) instead of the Redis service name. Inside Docker each container has its own localhost — they're isolated.

```
node_app container:
    127.0.0.1 → its own loopback  (no Redis here)
    redis     → DNS resolves to the redis container ✓
```

**Fix:** Change the Redis host in your app config from `localhost` to `redis` (the Compose service name):
```js
// wrong
const client = redis.createClient({ host: 'localhost', port: 6379 });

// correct
const client = redis.createClient({ url: 'redis://redis:6379' });
```

---

### `node_modules` not found inside container

```
Error: Cannot find module 'express'
```

**Why it happens:** A bind mount of the source code overlays the `node_modules` folder that was installed during `docker build`. The host directory (with no `node_modules`) wins.

```
Image layers:      /app/node_modules ✓  (installed in Dockerfile)
Bind mount:        /app              ←  host dir (no node_modules)
                                        node_modules gets hidden!
```

**Fix:** Use an anonymous volume to protect `node_modules`:
```yaml
volumes:
  - ./app:/app             # bind mount source
  - /app/node_modules      # anonymous volume shields node_modules from the bind mount
```

---

### Cache always shows miss (Redis not persisting between requests)

**Debugging:**
```bash
docker exec -it redis-container redis-cli KEYS "*"    # see what's cached
docker exec -it redis-container redis-cli TTL mykey   # check TTL
```

If Redis restarts between requests (container crash), the in-memory store resets. Add a named volume to persist Redis data across restarts:
```yaml
redis:
  volumes:
    - redis-data:/data
  command: redis-server --appendonly yes

volumes:
  redis-data:
```

---

## Project 04 — WordPress + MySQL

### WordPress shows "Error establishing a database connection"

**Why it happens:** WordPress can't reach MySQL. Most common causes:

1. Wrong `WORDPRESS_DB_PASSWORD` / `MYSQL_ROOT_PASSWORD` in `.env`
2. MySQL not ready yet when WordPress starts
3. Service name mismatch

**Debugging:**
```bash
docker compose logs mysql           # look for "ready for connections"
docker compose logs wordpress       # look for the actual error

# Test connectivity from WordPress container
docker exec -it wordpress-container mysql -h mysql -u root -p
```

**Fix (most common — password mismatch):**
```bash
docker compose down -v             # wipe volumes (MySQL ignores env on existing volume)
# Edit .env so all passwords match
docker compose up
```

---

### MySQL "Access denied for user 'root'@'localhost'"

```
ERROR 1045 (28000): Access denied for user 'root'@'172.18.0.3' (using password: YES)
```

**Why it happens:** MySQL was previously initialised with a different password (old named volume).

**Fix:** Same as above — `docker compose down -v` then restart with correct `.env`.

---

### WordPress setup wizard restarts every time

**Why it happens:** `wp-content` volume was deleted (`make clean`) — WordPress treats a missing `wp-config.php` as a fresh install.

**Fix:**
- Use `make down` (keeps volumes) when you just want to stop the stack
- Use `make clean` only when you intentionally want to wipe and start over

---

### WordPress loads but plugins/themes look broken (CSS missing)

**Why it happens:** WordPress stored its URL during setup. If you change the host port, the stored URL no longer matches.

**Fix:** `make clean` and redo the setup wizard, or update `siteurl` and `home` in the database:
```bash
docker exec -it mysql-container mysql -u root -p wordpress_db
# In MySQL:
UPDATE wp_options SET option_value='http://localhost:8080' WHERE option_name IN ('siteurl','home');
```

---

## Project 05 — Flask + MongoDB + Nginx

### Flask app stays "unhealthy": "wget: executable file not found"

```
dependency failed to start: container 05-flask-mongo-nginx-app-1 is unhealthy
```

When inspecting the healthcheck log:
```
OCI runtime exec failed: exec failed: unable to start container process:
exec: "wget": executable file not found in $PATH
```

**Why it happens:** The Flask app runs inside `python:3.12-slim`, which is a minimal Debian image with no networking tools (`wget`, `curl`) installed. The `docker-compose.yml` healthcheck that calls `wget` therefore fails immediately.

```
python:3.12-slim runtime image:
  ✓  python3, pip
  ✗  wget  (not installed — use Python's stdlib instead)
  ✗  curl  (not installed)
```

**Fix:** Replace the `wget` healthcheck with a Python one-liner that uses the built-in `urllib`:
```yaml
healthcheck:
  test:
    - "CMD"
    - "python3"
    - "-c"
    - "import urllib.request; urllib.request.urlopen('http://localhost:5000/api/health')"
  interval: 15s
  timeout: 5s
  retries: 5
  start_period: 10s
```

Alternatively, install `curl` in the Dockerfile runtime stage:
```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
```

---

### Port 80 already in use — host nginx intercepts all requests

```
# docker compose up succeeds — no error
# but every curl returns:
<html><head><title>404 Not Found</title></head>
<body><center><h1>404 Not Found</h1></center>
<hr><center>nginx/1.24.0 (Ubuntu)</center>   ← host nginx, not the container!
```

**Why it happens:** This project binds to host port 80 by default. If your machine already has a system nginx (or any other service) listening on port 80, Docker Compose v2.20+ (which uses iptables NAT instead of docker-proxy) may not block start-up, but outbound `localhost:80` connections still reach the host process — not the container.

```
Host: system nginx listening on 0.0.0.0:80 (started before Docker)
      │
      ▼
curl http://localhost:80  ──► loopback interface ──► host nginx (PID 218)
                                                       responds with its own 404
                                NOT routed to Docker container
```

**Debugging:**
```bash
# Check what's listening on port 80
ss -tlnp | grep ':80'

# Check which nginx version responds
curl -s -I http://localhost | grep Server
# If "nginx/1.24.0 (Ubuntu)" → host process, not the container

# Confirm the container works in isolation
docker inspect 05-flask-mongo-nginx-nginx-1 | grep -A2 Ports
docker exec 05-flask-mongo-nginx-nginx-1 wget -qO- http://127.0.0.1/api/health
```

**Fix — use a different host port:**
```yaml
# docker-compose.yml
services:
  nginx:
    ports:
      - "8081:80"   # change from "80:80"
```

Then access the app at `http://localhost:8081`.

**Fix — stop the host nginx (if you own it):**
```bash
sudo systemctl stop nginx
sudo systemctl disable nginx   # prevent it starting on next boot
docker compose restart nginx
```

---

### Nginx returns "502 Bad Gateway"

```
502 Bad Gateway
nginx/1.25.x
```

**Why it happens:** Nginx is proxying to `flask:5000` but Flask is not running or hasn't started yet.

```
Browser → Nginx → flask:5000  ──► connection refused
                                  Flask not up yet (or crashed)
```

**Debugging:**
```bash
docker compose ps                   # is flask_app healthy?
docker compose logs flask_app       # look for startup errors or tracebacks
docker exec -it nginx-container curl -s http://flask:5000/api/health   # test internal reach
```

**Fix:**
```bash
docker compose up --build          # rebuild Flask image if you changed code
docker compose restart flask_app   # restart just Flask
```

---

### Flask can't connect to MongoDB: "ServerSelectionTimeoutError"

```
flask_app | pymongo.errors.ServerSelectionTimeoutError: mongo:27017:
  [Errno 111] Connection refused, Timeout: 30s
```

**Why it happens:** Flask started before MongoDB finished its init sequence, or the service name in the connection string doesn't match the Compose service name.

**Fix — check the connection string:**
```python
# wrong
client = pymongo.MongoClient("localhost", 27017)

# correct (use service name from docker-compose.yml)
client = pymongo.MongoClient("mongo", 27017)
```

**Fix — wait for MongoDB with a healthcheck:**
```yaml
mongo:
  healthcheck:
    test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
    interval: 10s
    retries: 5

flask_app:
  depends_on:
    mongo:
      condition: service_healthy
```

---

### MongoDB authentication error

```
pymongo.errors.OperationFailure: Authentication failed.
```

**Why it happens:** `MONGO_INITDB_ROOT_USERNAME` / `MONGO_INITDB_ROOT_PASSWORD` don't match what the app uses, or MongoDB was initialised without auth (old volume) and now you added auth.

**Fix:**
```bash
docker compose down -v             # drop the old volume
# Ensure .env has consistent credentials
docker compose up
```

---

### Seed script does nothing / duplicate data on every `make up`

**Why it happens:** The seed script runs every time without checking if data already exists.

**Fix:** Add an idempotency check in the seed script before inserting:
```python
if db.books.count_documents({}) == 0:
    db.books.insert_many(seed_data)
```

Or run the seed explicitly once: `make seed` (instead of having it run automatically at startup).

---

### Nginx config change not picked up after `make up`

**Why it happens:** Nginx reads the config file at startup. If you mounted the config as a bind mount and changed it, Nginx still uses the old config in memory.

**Fix:**
```bash
docker compose exec nginx nginx -s reload     # hot-reload without restarting
# OR
docker compose restart nginx
```

---

## General "I changed code but the container still runs the old version"

This is the most common beginner confusion across all projects.

```
You edited app.py on the host
       │
       ▼
docker compose up    ← did NOT rebuild the image
       │
       ▼
Container runs OLD image layer (your edit is not there!)
```

**Fix:**
```bash
docker compose up --build          # rebuild images before starting
# Or separately:
docker compose build
docker compose up
```

For development, use a bind mount so code changes are reflected instantly without rebuilding:
```yaml
volumes:
  - ./app:/app     # host code → container (live edit)
```

---

## Cross-Reference

| Error type | Where to learn more |
|---|---|
| Networking (ECONNREFUSED, 502) | [05 — Networking](../05-networking/README.md) |
| Volume/permission issues | [04 — Volumes](../04-volumes/README.md) |
| Healthchecks / `depends_on` | [Compose reference](../03-docker-compose/compose-reference.md) |
| Build cache / layer issues | [Image layers](../01-basics/image-layers.md) |
| Env variable handling | [Env and overrides](../03-docker-compose/env-and-override.md) |
| General Docker errors | [Troubleshooting README](./README.md) |
