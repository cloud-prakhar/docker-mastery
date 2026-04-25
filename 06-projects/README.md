# 06 — Projects

End-to-end mini projects that combine everything: Dockerfiles, Compose, volumes, and networking.

## Projects

| Project | Stack | Key Concepts Practised |
|---|---|---|
| [01 — Nginx Static Site](./01-nginx-static/) | Nginx | Bind mounts, custom Nginx config, healthcheck |
| [02 — Flask + PostgreSQL](./02-flask-postgres/) | Python, Flask, PostgreSQL | Multi-container, named volumes, `depends_on` with healthcheck |
| [03 — Node.js + Redis](./03-node-redis/) | Node.js, Express, Redis | Cache-aside pattern, named networks, multi-stage Dockerfile |
| [04 — WordPress + MySQL](./04-wordpress-mysql/) | PHP, WordPress, MySQL | Real-world 2-tier stack, secret injection via env |
| [05 — Flask + MongoDB + Nginx](./05-flask-mongo-nginx/) | Python, Flask, MongoDB, Nginx | 3-tier architecture, reverse proxy, `internal` network, seed scripts |

## Theory Each Project Reinforces

Before attempting a project, make sure you've read the linked theory:

| Project | Read First |
|---|---|
| 01 — Nginx Static | [Bind mounts](../04-volumes/README.md) · [First container](../01-basics/first-container.md) |
| 02 — Flask + Postgres | [Named volumes](../04-volumes/README.md) · [Compose networking](../05-networking/README.md#compose-networking) · [Healthchecks](../03-docker-compose/compose-reference.md#healthcheck) |
| 03 — Node + Redis | [Multi-stage builds](../01-basics/dockerfile-reference.md#multi-stage-build-example) · [User-defined networks](../05-networking/README.md#user-defined-bridge-networks-recommended) |
| 04 — WordPress + MySQL | [Env files](../03-docker-compose/env-and-override.md) · [Volume patterns](../04-volumes/volume-patterns.md) |
| 05 — Flask + Mongo + Nginx | [Network segmentation](../05-networking/README.md#compose-networking) · [Reverse proxy pattern](../05-networking/network-deep-dive.md) · [Union filesystem](../04-volumes/README.md#why-containers-lose-data-the-union-filesystem) |

## Recommended Order

Do them in order if you're learning sequentially. Each project introduces one new architectural pattern:

```
01 (single container + bind mount)
  └─► 02 (add a database + healthcheck)
        └─► 03 (add a cache + multi-stage build)
              └─► 04 (official complex image + secrets)
                    └─► 05 (full 3-tier with reverse proxy + network isolation)
```

## How to Use Each Project

Every project folder contains:
- `docker-compose.yml` — the stack definition
- `Dockerfile` (where applicable) — custom image build
- `Makefile` — shortcuts (`make up`, `make down`, `make logs`)
- `.env.example` — required environment variables (copy to `.env` before running)
- `README.md` — project-specific instructions and architecture diagram

```bash
cd 01-nginx-static
cp .env.example .env     # copy and edit as needed
make up                  # start the stack
make logs                # follow logs
make down                # tear down (volumes preserved)
make clean               # tear down + delete volumes
```
