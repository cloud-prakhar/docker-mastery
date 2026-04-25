# System Commands

## Disk Usage

```bash
docker system df           # summary: images, containers, volumes, build cache
docker system df -v        # verbose: per-image and per-volume breakdown
```

Example output:
```
TYPE            TOTAL   ACTIVE  SIZE      RECLAIMABLE
Images          12      3       2.1GB     1.6GB (76%)
Containers      5       2       120MB     80MB (66%)
Local Volumes   8       3       950MB     300MB (31%)
Build Cache     45      0       1.2GB     1.2GB
```

## Pruning (Cleanup)

```bash
# Remove stopped containers
docker container prune

# Remove dangling images (<none>:<none>)
docker image prune

# Remove all unused images (not referenced by any container)
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove unused networks
docker network prune

# Remove everything unused at once
docker system prune

# Nuclear option — remove everything including volumes and all images
docker system prune -a --volumes
```

Add `-f` to skip the confirmation prompt in scripts.

## System Info

```bash
docker info                # engine info: version, storage driver, OS, resources
docker version             # client and server version details
docker system events       # real-time event stream (container start/stop, etc.)
docker system events --since 1h --filter event=start
```

## Context (Managing Multiple Docker Hosts)

```bash
docker context ls                         # list contexts
docker context create remote --docker "host=ssh://user@host"
docker context use remote                 # switch context
docker context use default                # back to local
```

## Useful Cleanup One-Liners

```bash
# Remove all stopped containers
docker rm $(docker ps -aq --filter status=exited)

# Remove all untagged images
docker rmi $(docker images -q --filter dangling=true)

# Kill all running containers
docker kill $(docker ps -q)

# Remove everything (containers, images, volumes, networks)
docker stop $(docker ps -q) 2>/dev/null; docker system prune -af --volumes
```
