# Project 02 — Flask + PostgreSQL

A minimal Python Flask API backed by PostgreSQL, demonstrating multi-container orchestration with health checks and named volumes.

## What You'll Learn
- Multi-stage Dockerfile for Python
- `depends_on` with `condition: service_healthy`
- Named volumes for database persistence
- Environment variable injection via `.env`

## Quick Start

```bash
cp .env.example .env
make up
# API available at http://localhost:5000
curl http://localhost:5000/health
curl http://localhost:5000/users
make down
```

## Structure

```
02-flask-postgres/
├── app/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
├── db/
│   └── init.sql
├── docker-compose.yml
├── .env.example
└── Makefile
```
