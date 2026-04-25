# Docker Commands Cheatsheet

## Images

```bash
docker build -t NAME:TAG .            # build image
docker build --no-cache -t NAME .     # build without cache
docker pull IMAGE:TAG                 # pull from registry
docker push NAME:TAG                  # push to registry
docker images                         # list images
docker rmi IMAGE                      # remove image
docker image prune -a                 # remove all unused images
docker tag SOURCE TARGET              # tag an image
docker history IMAGE                  # layer history
docker save IMAGE | gzip > img.tar.gz # export image
docker load < img.tar.gz              # import image
```

## Containers

```bash
docker run IMAGE                      # create + start
docker run -d IMAGE                   # detached
docker run -it IMAGE sh               # interactive shell
docker run --rm IMAGE                 # auto-remove on exit
docker run -p HOST:CONTAINER IMAGE    # publish port
docker run -v HOST:CONTAINER IMAGE    # bind mount
docker run -e KEY=VAL IMAGE           # set env var
docker run --name NAME IMAGE          # named container
docker run --network NET IMAGE        # join network
docker run --restart always IMAGE     # auto-restart
docker ps                             # list running
docker ps -a                          # list all
docker stop CONTAINER                 # graceful stop
docker kill CONTAINER                 # force stop
docker rm CONTAINER                   # remove stopped
docker rm -f CONTAINER                # force remove
docker start CONTAINER                # start stopped
docker restart CONTAINER              # restart
docker exec -it CONTAINER sh          # shell in container
docker exec CONTAINER CMD             # run command
docker logs CONTAINER                 # view logs
docker logs -f CONTAINER              # follow logs
docker logs --tail 50 CONTAINER       # last 50 lines
docker cp SRC CONTAINER:DST           # copy to container
docker cp CONTAINER:SRC DST           # copy from container
docker inspect CONTAINER              # metadata JSON
docker stats                          # live resource usage
docker top CONTAINER                  # processes
docker port CONTAINER                 # port mappings
docker diff CONTAINER                 # filesystem changes
docker rename OLD NEW                 # rename container
docker pause CONTAINER                # freeze
docker unpause CONTAINER              # unfreeze
```

## Volumes

```bash
docker volume create NAME             # create named volume
docker volume ls                      # list volumes
docker volume inspect NAME            # details
docker volume rm NAME                 # remove
docker volume prune                   # remove unused
```

## Networks

```bash
docker network create NAME            # create network
docker network ls                     # list networks
docker network inspect NAME           # details
docker network connect NET CONTAINER  # attach container
docker network disconnect NET CONTAINER # detach
docker network rm NAME                # remove
docker network prune                  # remove unused
```

## System

```bash
docker info                           # engine info
docker version                        # version info
docker system df                      # disk usage
docker system df -v                   # verbose disk usage
docker system prune                   # remove unused resources
docker system prune -a --volumes      # remove everything unused
docker system events                  # real-time events
```

## Registry

```bash
docker login                          # login to Docker Hub
docker login REGISTRY                 # login to private registry
docker logout                         # logout
docker search IMAGE                   # search Docker Hub
```
