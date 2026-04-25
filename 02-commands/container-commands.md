# Container Commands

## docker run — Create and Start

```bash
docker run [OPTIONS] IMAGE [COMMAND]
```

| Option | Description |
|---|---|
| `-d` | Detached (background) |
| `-it` | Interactive + pseudo-TTY (for shells) |
| `--rm` | Remove container on exit |
| `-p HOST:CONTAINER` | Publish port |
| `-P` | Publish all exposed ports to random host ports |
| `--name NAME` | Assign a name |
| `-e KEY=VAL` | Set environment variable |
| `--env-file FILE` | Load env vars from file |
| `-v HOST:CONTAINER` | Bind mount a volume |
| `--network NETWORK` | Connect to a network |
| `--restart POLICY` | `no` / `always` / `on-failure` / `unless-stopped` |
| `--memory 512m` | Memory limit |
| `--cpus 1.5` | CPU limit |
| `--user UID:GID` | Run as specific user |
| `--read-only` | Read-only root filesystem |

### Examples

```bash
# Nginx web server
docker run -d -p 8080:80 --name web nginx:alpine

# Interactive Alpine shell
docker run -it --rm alpine sh

# PostgreSQL with env vars and named volume
docker run -d \
  --name postgres \
  -e POSTGRES_PASSWORD=secret \
  -e POSTGRES_DB=mydb \
  -v pgdata:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:16-alpine

# Run a one-off command
docker run --rm -v $(pwd):/work -w /work node:20-alpine npm install
```

## Lifecycle Commands

```bash
docker start CONTAINER      # start a stopped container
docker stop CONTAINER       # graceful stop (SIGTERM → SIGKILL after 10s)
docker kill CONTAINER       # immediate stop (SIGKILL)
docker restart CONTAINER    # stop + start
docker pause CONTAINER      # freeze (SIGSTOP)
docker unpause CONTAINER    # unfreeze
```

## Listing Containers

```bash
docker ps                          # running containers
docker ps -a                       # all containers (incl. stopped)
docker ps -q                       # only IDs
docker ps --filter status=exited   # filter by status
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

## Removing Containers

```bash
docker rm CONTAINER                # remove stopped container
docker rm -f CONTAINER             # force-remove running container
docker rm $(docker ps -aq)         # remove all stopped containers
docker container prune             # same, with confirmation prompt
```

## Logs

```bash
docker logs CONTAINER              # print all logs
docker logs -f CONTAINER           # follow (stream) logs
docker logs --tail 50 CONTAINER    # last 50 lines
docker logs --since 10m CONTAINER  # logs from last 10 minutes
docker logs -t CONTAINER           # include timestamps
```

## Exec — Run Commands in a Running Container

```bash
docker exec -it CONTAINER sh       # open a shell
docker exec CONTAINER ls /app      # run a one-off command
docker exec -e DEBUG=1 CONTAINER python manage.py shell
docker exec -u root CONTAINER bash # exec as a specific user
```

## Copying Files

```bash
docker cp CONTAINER:/app/log.txt ./local-log.txt   # container → host
docker cp ./config.json CONTAINER:/app/config.json  # host → container
```

## Inspecting Containers

```bash
docker inspect CONTAINER                     # full JSON metadata
docker inspect -f '{{.NetworkSettings.IPAddress}}' CONTAINER  # extract field
docker top CONTAINER                         # running processes
docker stats                                 # live resource usage (all)
docker stats CONTAINER                       # live resource usage (one)
docker port CONTAINER                        # port mappings
docker diff CONTAINER                        # changed files vs image
```
