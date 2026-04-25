# Project 04 — WordPress + MySQL

The classic WordPress stack: PHP app + MySQL database. A realistic example of a production-like Compose setup with secrets management.

## What You'll Learn
- Official images with complex configuration
- MySQL healthchecks and init scripts
- Named volumes for both app and DB data
- Secrets via environment variables

## Quick Start

```bash
cp .env.example .env
# Edit .env and set strong passwords
make up
# WordPress at http://localhost:8080
# Complete the WordPress setup wizard
make down       # stops containers (data preserved)
make clean      # stops + removes volumes (data destroyed)
```

## Structure

```
04-wordpress-mysql/
├── docker-compose.yml
├── .env.example
└── Makefile
```
