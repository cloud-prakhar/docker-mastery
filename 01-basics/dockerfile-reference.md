# Dockerfile Instruction Reference

A Dockerfile is a text file with instructions that Docker executes top-to-bottom to build an image. Each instruction creates a new **layer**.

## Instructions

### FROM
```dockerfile
FROM ubuntu:22.04
FROM python:3.12-slim AS builder   # named stage for multi-stage builds
```
Always the first instruction. Specifies the base image.

### WORKDIR
```dockerfile
WORKDIR /app
```
Sets the working directory for subsequent RUN, COPY, CMD, ENTRYPOINT instructions. Creates the directory if it doesn't exist.

### COPY vs ADD
```dockerfile
COPY src/ /app/src/           # preferred: explicit copy
ADD archive.tar.gz /app/      # ADD can also extract tar and fetch URLs
```
Prefer `COPY` — it's transparent. Use `ADD` only when you need tar extraction.

### RUN
```dockerfile
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
```
Executes a command during the build. Chain commands with `&&` and clean up in the **same layer** to keep image size down.

### ENV
```dockerfile
ENV APP_ENV=production \
    PORT=8080
```
Sets environment variables available at build time and runtime.

### ARG
```dockerfile
ARG VERSION=1.0
RUN echo "Building version $VERSION"
```
Build-time variable only — not available in the running container.

### EXPOSE
```dockerfile
EXPOSE 8080
```
Documents which port the app listens on. Does **not** publish the port — use `-p` with `docker run` for that.

### VOLUME
```dockerfile
VOLUME ["/data"]
```
Creates a mount point. Docker will create an anonymous volume here if no volume is mounted at runtime.

### USER
```dockerfile
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser
```
Switches to a non-root user. Always do this for production images.

### CMD vs ENTRYPOINT

| | CMD | ENTRYPOINT |
|---|---|---|
| Purpose | Default command (overridable) | Fixed executable |
| Overridden by | `docker run image <cmd>` | `docker run --entrypoint` |
| Typical use | Default args to entrypoint | The main process |

```dockerfile
# Pattern 1: CMD only (simple scripts)
CMD ["python", "app.py"]

# Pattern 2: ENTRYPOINT + CMD (entrypoint is fixed, CMD provides defaults)
ENTRYPOINT ["gunicorn"]
CMD ["--workers", "4", "app:app"]
```

Always use **exec form** (`["executable", "arg"]`) not shell form (`executable arg`) — exec form doesn't spawn a shell and handles signals correctly.

## Multi-Stage Build Example

```dockerfile
# Stage 1: build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: runtime (only the built output, no dev deps)
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

The final image only contains the nginx + built files — no Node.js, no source code.

## .dockerignore

Create a `.dockerignore` alongside your `Dockerfile` to exclude files from the build context:

```
node_modules/
.git/
*.log
.env
dist/
```

Smaller build context = faster builds and smaller images.

## Image Size Tips

1. Use `-slim` or `-alpine` base images
2. Combine `RUN` commands to reduce layers
3. Remove package manager caches in the same `RUN` step
4. Use multi-stage builds to leave build tools out of the final image
5. Use `.dockerignore` to exclude unnecessary files
