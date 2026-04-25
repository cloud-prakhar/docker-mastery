# Project 01 — Nginx Static Site

Serve static HTML/CSS/JS from a bind-mounted directory with a custom Nginx config.

## What You'll Learn
- Bind mounts for live file editing
- Custom Nginx configuration
- Multi-stage build for production (optional)

## Quick Start

```bash
make up
# open http://localhost:8080
make down
```

## Structure

```
01-nginx-static/
├── docker-compose.yml
├── nginx.conf
├── html/
│   └── index.html
└── Makefile
```

## Key Concepts Demonstrated

**Bind mount** — the `html/` directory is mounted into the container at `/usr/share/nginx/html`. Edit files on the host; Nginx serves the changes instantly without rebuilding.

**Custom config** — `nginx.conf` is mounted read-only at `/etc/nginx/conf.d/default.conf`, overriding the default Nginx configuration.
