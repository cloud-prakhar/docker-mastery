# Project 03 — Node.js + Redis

An Express.js API that caches responses in Redis. Demonstrates container-to-container communication, named networks, and the caching pattern.

## What You'll Learn
- Node.js multi-stage Dockerfile
- Redis as an in-memory cache
- Named networks for service isolation
- Cache-aside pattern

## Quick Start

```bash
make up
# API at http://localhost:3000
curl http://localhost:3000/data       # first call: cache miss (slow)
curl http://localhost:3000/data       # second call: cache hit (fast)
curl http://localhost:3000/cache/flush  # clear the cache
make down
```

## Structure

```
03-node-redis/
├── app/
│   ├── Dockerfile
│   ├── package.json
│   └── index.js
├── docker-compose.yml
├── .env.example
└── Makefile
```
