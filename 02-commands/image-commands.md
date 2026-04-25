# Image Commands

## Building Images

```bash
docker build -t myapp:1.0 .                  # build from ./Dockerfile
docker build -t myapp:1.0 -f path/Dockerfile . # custom Dockerfile path
docker build --no-cache -t myapp:latest .    # bypass layer cache
docker build --build-arg VERSION=2.0 -t myapp .  # pass build args
docker build --target builder -t myapp-build .   # build up to a stage
```

## Listing Images

```bash
docker images                           # all local images
docker images -a                        # include intermediate layers
docker images nginx                     # filter by name
docker images --filter dangling=true    # untagged images (<none>)
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
```

## Tagging

```bash
docker tag myapp:1.0 myapp:latest                    # add alias tag
docker tag myapp:1.0 registry.example.com/myapp:1.0  # tag for a registry
```

Tag format: `[REGISTRY/][NAMESPACE/]NAME[:TAG]`  
Default tag is `latest` if omitted.

## Pushing and Pulling

```bash
# Login to Docker Hub
docker login

# Login to a private registry
docker login registry.example.com

# Push
docker push myusername/myapp:1.0

# Pull
docker pull redis:7-alpine
docker pull --platform linux/amd64 nginx:alpine  # force platform
```

## Removing Images

```bash
docker rmi IMAGE                     # remove by name or ID
docker rmi -f IMAGE                  # force (remove even if tagged multiple times)
docker rmi $(docker images -q)       # remove all local images
docker image prune                   # remove dangling (untagged) images
docker image prune -a                # remove all unused images
```

## Inspecting Images

```bash
docker inspect IMAGE                        # full metadata JSON
docker history IMAGE                        # layer history and sizes
docker inspect --format='{{.Os}}/{{.Architecture}}' IMAGE
```

## Saving and Loading Images (offline transfer)

```bash
docker save myapp:1.0 | gzip > myapp.tar.gz         # export to tarball
docker load < myapp.tar.gz                           # import from tarball
```

Useful for air-gapped environments.

## Image Naming Convention

```
docker.io/library/nginx:alpine
│         │       │     │
│         │       │     └─ Tag
│         │       └─ Image name
│         └─ Namespace (official images use "library")
└─ Registry (default: docker.io)
```

Common registries:
- `docker.io` — Docker Hub (default)
- `ghcr.io` — GitHub Container Registry
- `public.ecr.aws` — AWS ECR Public
- `gcr.io` — Google Container Registry

> For a full beginner guide covering Docker Hub accounts, tag conventions, Official Images, rate limits, and private registries, see [docker-hub-and-registries.md](../01-basics/docker-hub-and-registries.md).
