# Docker Mastery

A comprehensive Docker learning repository covering commands, Docker Compose, core concepts, networking, volumes, and hands-on mini projects. Built as a practical guide for mastering containerization with real-world DevOps use cases.

## Contents

| Section | What You'll Learn |
|---|---|
| [01 — Basics](./01-basics/) | Containers vs VMs, hypervisors, Docker architecture, image layers, Docker Hub & registries, Dockerfiles, DevOps roadmap |
| [02 — Commands](./02-commands/) | Full Docker CLI reference — containers, images, system commands |
| [03 — Docker Compose](./03-docker-compose/) | Multi-container orchestration, YAML spec, env files, overrides |
| [04 — Volumes](./04-volumes/) | Union filesystem theory, bind mounts, named volumes, tmpfs, backup patterns |
| [05 — Networking](./05-networking/) | Bridge, host, overlay networks; container DNS; iptables internals |
| [06 — Projects](./06-projects/) | Real-world stacks: Nginx, Flask+Postgres, Node+Redis, WordPress, Flask+Mongo+Nginx |
| [07 — Troubleshooting](./07-troubleshooting/) | Common Docker errors + project-specific fixes for beginners |
| [Cheatsheets](./cheatsheets/) | Quick-reference cards — commands, Compose, Dockerfile |

## New to Docker? Start Here

If you're coming from zero, read these first before touching a command:

1. [What is a hypervisor and how Docker differs](./01-basics/virtualization-vs-containers.md) — the theory behind containers
2. [Your first container — step by step](./01-basics/first-container.md) — hands-on from zero
3. [Docker Hub and registries](./01-basics/docker-hub-and-registries.md) — where images come from and how to publish your own
4. [Docker in the DevOps roadmap](./01-basics/devops-roadmap.md) — where this fits in your career

## Prerequisites

- Linux, macOS, or Windows with WSL2
- Basic command-line familiarity

## Quick Start

```bash
# Verify Docker is installed
docker --version
docker compose version

# Run your first container
docker run --rm hello-world
```

## Learning Path

Follow the numbered sections in order for a structured experience, or jump to any topic if you need a specific concept.

```
01-basics → 02-commands → 03-docker-compose → 04-volumes → 05-networking → 06-projects
```

> Each section README links to deeper theory files and cross-references related sections.
> Cheatsheets are standalone quick-reference cards — bookmark them once you're past the basics.
