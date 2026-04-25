# Dockerfile Cheatsheet

## Instructions

```dockerfile
FROM image:tag                    # base image (must be first)
FROM image:tag AS stage           # named stage for multi-stage build

WORKDIR /path                     # set working directory (creates if absent)

COPY src dest                     # copy files from build context
COPY --from=stage src dest        # copy from another build stage
ADD src dest                      # copy + extract tar / fetch URL

RUN command                       # run during build (shell form)
RUN ["executable", "arg"]         # run during build (exec form — preferred)

ENV KEY=VALUE                     # environment variable (build + runtime)
ARG NAME=default                  # build-time variable only

EXPOSE 8080                       # document the port (informational)
VOLUME ["/data"]                  # declare a mount point

USER name                         # switch user for subsequent instructions
USER uid:gid

LABEL key=value                   # metadata

CMD ["executable", "arg"]         # default command (overridable)
ENTRYPOINT ["executable"]         # fixed entrypoint

HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -f http://localhost/health

ONBUILD INSTRUCTION               # trigger for child images

SHELL ["/bin/sh", "-c"]           # change default shell for RUN
```

## Multi-Stage Build Template

```dockerfile
# Stage 1: build dependencies / compile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: minimal runtime image
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## .dockerignore

```
# Always include:
.git/
node_modules/
dist/
build/
*.log
.env
.env.*
!.env.example
__pycache__/
.venv/
*.pyc
.DS_Store
```

## Size Reduction Tips

```dockerfile
# 1. Use slim/alpine base images
FROM python:3.12-slim

# 2. Combine RUN commands — each RUN is a layer
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# 3. Copy dependency files before source (better caching)
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .        # only invalidates cache when source changes

# 4. Run as non-root
RUN addgroup -S app && adduser -S app -G app
USER app

# 5. Use multi-stage to exclude build tools from final image
```

## Build Commands

```bash
docker build -t name:tag .
docker build -t name:tag -f path/Dockerfile .
docker build --no-cache -t name:tag .
docker build --build-arg KEY=VALUE -t name:tag .
docker build --target STAGE -t name:tag .
docker build --platform linux/amd64,linux/arm64 -t name:tag .  # multi-arch
```
