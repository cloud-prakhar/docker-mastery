# 05 — Networking

Docker containers communicate through virtual networks managed by the Docker Engine.

## Why Container Networking Exists

A container runs as an **isolated process** with its own network namespace — from inside, it looks like a machine with only a loopback interface (`lo`). Without explicit networking, containers are dark islands that cannot reach the internet, your host, or each other.

```
Without networking:

  ┌─────────┐    ┌─────────┐    ┌─────────┐
  │  App    │    │   DB    │    │  Cache  │
  │ (blind) │    │ (blind) │    │ (blind) │
  └─────────┘    └─────────┘    └─────────┘
  Can't talk to each other or to the internet.

With a Docker network:

  ┌─────────┐    ┌─────────┐    ┌─────────┐
  │   App   │◄──►│   DB    │    │  Cache  │
  │         │◄──────────────────►         │
  └────┬────┘    └─────────┘    └─────────┘
       │
       │ (via NAT through host)
       ▼
   Internet
```

Docker networking is built on two Linux kernel features you already saw in the theory section:
- **Network namespaces** — each container gets its own isolated network stack (interfaces, routing table, ports)
- **Virtual ethernet pairs (veth)** — a virtual cable connecting a container's namespace to the host bridge

> Background: [Network namespaces and how the bridge works](./network-deep-dive.md) goes deep on the Linux internals.  
> Background: [Namespaces overview](../01-basics/virtualization-vs-containers.md#the-two-linux-features-that-make-this-possible) in 01-basics introduces the concept.

## Network Drivers

| Driver | Use Case |
|---|---|
| **bridge** | Default. Isolated network on a single host. Containers communicate by name. |
| **host** | Container shares host network stack. No isolation, max performance. Linux only. |
| **none** | No networking. Fully isolated. |
| **overlay** | Multi-host networking (Docker Swarm). |
| **macvlan** | Assign a MAC address to the container — appears as a physical device on the network. |

## Default Bridge Network

Every container added to Docker gets attached to the default `bridge` network unless otherwise specified.

```bash
docker network ls
# NETWORK ID   NAME      DRIVER    SCOPE
# abc123       bridge    bridge    local
# def456       host      host      local
# ghi789       none      null      local
```

Limitation: containers on the default bridge network **cannot resolve each other by name** — only by IP. Use user-defined networks instead.

## User-Defined Bridge Networks (recommended)

```bash
docker network create app-net
docker run -d --name web --network app-net nginx:alpine
docker run -d --name db  --network app-net postgres:16-alpine

# Containers can now reach each other by name:
docker exec -it web ping db       # works!
```

Advantages over default bridge:
- Automatic DNS — containers resolve each other by service name
- Better isolation
- Can connect/disconnect containers at runtime

## Network Commands

```bash
docker network ls                           # list all networks
docker network create mynet                 # create a bridge network
docker network create --driver host hostnet # host network (named)
docker network inspect mynet               # details: containers, subnet, gateway
docker network connect mynet CONTAINER     # attach running container to network
docker network disconnect mynet CONTAINER  # detach
docker network rm mynet                    # remove (must have no containers)
docker network prune                       # remove all unused networks
```

## Container DNS

Within a user-defined network, Docker runs an embedded DNS server. Containers look up each other by:
- Container name (`--name`)
- Service name (in Compose)
- Network alias (`--network-alias`)

```bash
docker run -d --name api --network app-net --network-alias backend myapp
# Now reachable as both "api" and "backend" on app-net
```

## Port Publishing

```bash
-p 8080:80              # all interfaces, host 8080 → container 80
-p 127.0.0.1:8080:80   # localhost only
-p 80                   # random host port → container 80
-P                      # publish all EXPOSED ports to random host ports
```

## Compose Networking

Compose creates one network per project (named `<project>_default`) and connects all services to it automatically. Services resolve each other by their service name.

```yaml
services:
  web:
    image: nginx
    # can reach "db" and "cache" by name

  db:
    image: postgres:16

  cache:
    image: redis:7
```

For segmentation, define explicit networks:

```yaml
services:
  nginx:
    networks: [frontend]

  app:
    networks: [frontend, backend]

  db:
    networks: [backend]

networks:
  frontend:
  backend:
    internal: true    # no outbound internet from backend
```

## Files in This Section

- [network-deep-dive.md](./network-deep-dive.md) — iptables, namespaces, DNS internals

## Next

→ [06 — Projects](../06-projects/)
