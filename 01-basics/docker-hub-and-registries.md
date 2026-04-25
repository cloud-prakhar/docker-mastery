# Docker Hub and Container Registries

> Every time you run `docker pull nginx` or `FROM python:3.12-slim`, you are downloading an image from a **registry**. This guide explains what registries are, how Docker Hub works, how image naming actually functions, and how to publish your own images.

---

## 1. What is a Container Registry?

A container registry is a **remote storage and distribution system for Docker images**. Think of it like GitHub, but for images instead of source code.

```
Your machine                   Registry (e.g. Docker Hub)
─────────────                  ──────────────────────────
docker build →  local image    
docker push  →──────────────►  stores image (by layer)
docker pull  ◄──────────────── serves image (layer by layer)
docker run   →  pulls if not cached, then starts container
```

Without a registry, sharing an image would require copying a tarball manually (`docker save` / `docker load`). Registries make images universally accessible.

---

## 2. Docker Hub

**Docker Hub** (`hub.docker.com`) is the default public registry that Docker uses. When you type `docker pull nginx`, Docker silently expands that to `docker pull docker.io/library/nginx:latest` and fetches from Docker Hub.

### What Docker Hub provides

```
Docker Hub
│
├── Public images        Free to pull, anyone can access
├── Private repositories Free tier: 1 private repo; paid: unlimited
├── Automated builds     Connects to GitHub; rebuilds on push
├── Webhooks             Notify external services on push
├── Teams & Orgs         Access control for company accounts
└── Image scanning       Basic vulnerability scanning (paid)
```

### Image categories on Docker Hub

| Category | Who publishes | Trust level | Example |
|---|---|---|---|
| **Official Images** | Docker + upstream maintainers | Highest — audited by Docker | `nginx`, `python`, `postgres` |
| **Verified Publisher** | ISVs vetted by Docker | High — company-backed | `bitnami/nginx`, `elastic/elasticsearch` |
| **Community images** | Anyone | Variable — inspect before use | `myusername/myapp` |

**Official Images** are the ones you'll use most as a learner. They have no username prefix:

```bash
docker pull nginx          # Official Image (maintained by Docker + Nginx team)
docker pull python         # Official Image
docker pull myuser/myapp   # Community image (belongs to "myuser")
```

---

## 3. How Image Naming Works

Every Docker image has a fully qualified name. Docker fills in defaults when you use shorthand.

### Full Format

```
[REGISTRY_HOST/][NAMESPACE/]NAME[:TAG][@DIGEST]
      │              │         │      │    │
      │              │         │      │    └─ Optional: exact content hash
      │              │         │      └─ Version label (default: latest)
      │              │         └─ Image name
      │              └─ User or organisation
      └─ Registry hostname (default: docker.io)
```

### Examples decoded

```
nginx
└─ expands to: docker.io/library/nginx:latest

python:3.12-slim
└─ expands to: docker.io/library/python:3.12-slim

myuser/myapp:1.0
└─ expands to: docker.io/myuser/myapp:1.0

ghcr.io/myorg/myapp:v2.3.1
└─ Registry:   ghcr.io  (GitHub Container Registry)
   Namespace:  myorg
   Name:       myapp
   Tag:        v2.3.1
```

### Understanding Tags

A **tag** is a mutable label pointing to an image. It can be moved to a new image at any time.

```
python:latest     ─► points to the newest Python release
python:3.12       ─► points to the latest 3.12.x patch
python:3.12.3     ─► points to exactly 3.12.3 (most stable)
python:3.12-slim  ─► 3.12 on a minimal Debian base
python:3.12-alpine─► 3.12 on Alpine Linux (~5x smaller)
python:3-slim     ─► latest Python 3.x slim
```

**Common tag suffixes you'll see:**

| Suffix | Meaning |
|---|---|
| *(none)* / `latest` | Full image, most recent |
| `slim` | Stripped Debian — removes docs, man pages, extras |
| `alpine` | Based on Alpine Linux (~5MB base vs ~120MB Debian) |
| `bookworm` / `bullseye` | Specific Debian release codename |
| `rc` / `beta` | Release candidate — not for production |
| `X.Y.Z` | Pinned patch version — most reproducible |

**Best practice for production:** pin to a specific version tag:
```dockerfile
# Unpredictable — "latest" moves with new releases
FROM python:latest

# Better — locked to major.minor
FROM python:3.12-slim

# Best — locked to exact patch version
FROM python:3.12.3-slim
```

### Pulling by Digest (immutable)

Tags are mutable — `python:3.12-slim` today may point to a different image tomorrow. A **digest** is the SHA256 hash of the image content and never changes.

```bash
# See the digest of an image
docker inspect python:3.12-slim --format '{{index .RepoDigests 0}}'
# python@sha256:a64f5d35e399e...

# Pull by digest — guaranteed identical image, forever
docker pull python@sha256:a64f5d35e399e...

# Use in Dockerfile for total reproducibility
FROM python@sha256:a64f5d35e399e...
```

---

## 4. Pulling Images

```bash
# Pull latest tag (default)
docker pull nginx

# Pull a specific tag
docker pull nginx:1.25-alpine

# Pull from a non-Hub registry
docker pull ghcr.io/myorg/myapp:v1.0

# Pull a specific architecture (useful on Apple Silicon)
docker pull --platform linux/amd64 python:3.12-slim

# See what was pulled
docker images nginx
```

### What Happens During a Pull

```
docker pull python:3.12-slim

Step 1: Docker reads the tag "python:3.12-slim"
        Expands to: docker.io/library/python:3.12-slim

Step 2: Contacts registry API
        GET https://registry-1.docker.io/v2/library/python/manifests/3.12-slim
        Response: list of layer digests that make up this image

Step 3: For each layer digest:
        - Check local cache (/var/lib/docker/overlay2/)
        - If cached → "Already exists" (skip download)
        - If not → download the layer (compressed tar)

Step 4: Decompress and store each layer
        Assemble the image manifest locally

3.12-slim: Pulling from library/python
a8b1c2d3e4f5: Already exists     ← Debian base (cached from another image)
b9c0d1e2f3a4: Pull complete       ← Python runtime
c1d2e3f4a5b6: Pull complete       ← pip and setuptools
Digest: sha256:a64f5d...
Status: Downloaded newer image for python:3.12-slim
```

---

## 5. Creating a Docker Hub Account and Pushing Your First Image

### Step 1: Create an account

Go to [hub.docker.com](https://hub.docker.com) and sign up. Your username becomes your namespace (e.g. `myusername`).

### Step 2: Log in from the terminal

```bash
docker login
# Username: myusername
# Password: (your password or access token)
# Login Succeeded
```

**Use an Access Token, not your password** (more secure):
Docker Hub → Account Settings → Security → New Access Token

```bash
docker login --username myusername
# Password: <paste access token>
```

Store credentials safely — Docker stores them in `~/.docker/config.json`.

### Step 3: Build your image

```bash
docker build -t myapp:1.0 .
```

### Step 4: Tag it with your Docker Hub namespace

```bash
# Format: docker tag LOCAL_IMAGE USERNAME/REPO:TAG
docker tag myapp:1.0 myusername/myapp:1.0
docker tag myapp:1.0 myusername/myapp:latest   # also tag as latest
```

### Step 5: Push to Docker Hub

```bash
docker push myusername/myapp:1.0
docker push myusername/myapp:latest

# Output:
# The push refers to repository [docker.io/myusername/myapp]
# a1b2c3d4e5f6: Pushed
# f7a8b9c0d1e2: Layer already exists
# 1.0: digest: sha256:xyz... size: 1234
```

Your image is now public at `hub.docker.com/r/myusername/myapp`.

### Step 6: Anyone can now pull it

```bash
docker pull myusername/myapp:1.0
docker run myusername/myapp:1.0
```

### Full Flow Diagram

```
Local machine                       Docker Hub
─────────────                       ──────────
docker build -t myapp:1.0 .
       │
       ▼
  local image: myapp:1.0
       │
docker tag myapp:1.0 myusername/myapp:1.0
       │
       ▼
  local image: myusername/myapp:1.0
       │
docker push myusername/myapp:1.0 ──────────────► hub.docker.com/r/myusername/myapp
                                                            │
                                              docker pull myusername/myapp:1.0
                                                            │
                                                   Colleague's machine
```

---

## 6. Public vs Private Registries

| Type | Examples | Cost | Use case |
|---|---|---|---|
| **Public cloud registry** | Docker Hub, GHCR | Free tier available | Open source, personal projects |
| **Private cloud registry** | AWS ECR, GCP Artifact Registry, Azure ACR | Pay per storage/transfer | Company images, CI/CD |
| **Self-hosted** | Harbor, Nexus, GitLab Registry | Infrastructure cost | Air-gapped, full control |

### When to use each

```
Open source project   → Docker Hub (public image, community access)
Company / startup     → AWS ECR or GCP Artifact Registry
                          (sits next to your cloud infra, fast pulls)
Regulated / air-gapped → Self-hosted Harbor inside your network
GitHub-native team    → GitHub Container Registry (ghcr.io)
                          (auth through GitHub tokens)
```

---

## 7. Other Registries at a Glance

### GitHub Container Registry (ghcr.io)

```bash
# Login with a GitHub Personal Access Token (PAT)
echo $GITHUB_TOKEN | docker login ghcr.io --username myuser --password-stdin

docker push ghcr.io/myorg/myapp:v1.0
```

Packages are linked to your GitHub repo and inherit its visibility (public/private).

### AWS Elastic Container Registry (ECR)

```bash
# Get a temporary login token (expires in 12h)
aws ecr get-login-password --region us-east-1 \
  | docker login --username AWS --password-stdin \
    123456789.dkr.ecr.us-east-1.amazonaws.com

docker tag myapp:1.0 123456789.dkr.ecr.us-east-1.amazonaws.com/myapp:1.0
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/myapp:1.0
```

ECR is the natural choice when deploying to ECS, EKS, or Fargate — pulls are free within the same AWS region.

### Google Artifact Registry (GAR)

```bash
gcloud auth configure-docker us-docker.pkg.dev
docker push us-docker.pkg.dev/my-project/my-repo/myapp:1.0
```

### Self-Hosted: Harbor

Harbor is the most popular open-source enterprise registry. It adds role-based access control, image scanning (Trivy), and replication on top of standard registry APIs.

```bash
# After deploying Harbor (e.g. via Helm on K8s):
docker login registry.mycompany.com
docker push registry.mycompany.com/team/myapp:1.0
```

---

## 8. Docker Hub Rate Limits

Docker Hub enforces pull rate limits for unauthenticated and free accounts:

| Account type | Pull limit |
|---|---|
| Unauthenticated | 100 pulls / 6 hours per IP |
| Free account (logged in) | 200 pulls / 6 hours |
| Pro / Team / Business | Unlimited |

This matters in **CI/CD pipelines** — shared CI runners often hit the unauthenticated limit within minutes.

**Fixes:**
1. Log in to Docker Hub in your CI pipeline
2. Mirror base images to your own registry (ECR/GAR) and pull from there
3. Use a registry mirror/pull-through cache

```bash
# In GitHub Actions — log in before pulling
- name: Log in to Docker Hub
  uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKERHUB_USERNAME }}
    password: ${{ secrets.DOCKERHUB_TOKEN }}
```

---

## 9. Searching for Images

### On the CLI

```bash
docker search nginx                     # search Docker Hub
docker search --filter is-official=true nginx
docker search --limit 5 python
```

### On Docker Hub website

Go to `hub.docker.com` and search. On each image page look for:
- **Pulls** count — higher = more community trust
- **Official Image** badge — maintained by Docker/upstream
- **Tags** tab — all available versions
- **Overview** tab — usage instructions

### Key things to check before using a community image

```
✓ Pull count > 1M  (widely used)
✓ Recently updated  (active maintenance)
✓ Dockerfile source linked  (transparent)
✓ Minimal layers  (smaller attack surface)
✗ Avoid: last updated 3+ years ago
✗ Avoid: no linked source, no description
```

---

## 10. Common Registry Workflows

### Workflow A: Personal project on Docker Hub

```bash
docker build -t myusername/myapp:1.0 .
docker push myusername/myapp:1.0
# Share the image name with anyone
```

### Workflow B: Team project with a private registry

```bash
# Tag with registry URL
docker build -t myapp:1.0 .
docker tag myapp:1.0 123456789.dkr.ecr.us-east-1.amazonaws.com/myapp:1.0

# Push
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/myapp:1.0

# Pull on another machine
docker pull 123456789.dkr.ecr.us-east-1.amazonaws.com/myapp:1.0
```

### Workflow C: CI/CD pipeline (GitHub Actions)

```yaml
# .github/workflows/docker.yml
name: Build and Push

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Log in to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          push: true
          tags: |
            myusername/myapp:latest
            myusername/myapp:${{ github.sha }}
```

Every merge to `main` builds a new image and pushes it tagged with `latest` and the Git commit SHA — so you can always roll back to any previous version.

---

## Summary

```
Concept           What to remember
────────────────────────────────────────────────────────────────────────
Registry          Remote server that stores and serves images
Docker Hub        The default public registry (docker.io)
Official Images   Audited, maintained images with no username prefix
Tag               Mutable label (nginx:alpine, python:3.12-slim)
Digest            Immutable SHA256 hash — use for reproducible builds
docker pull       Download image layers from registry to local cache
docker push       Upload local image layers to registry
docker login      Authenticate with a registry
Namespace         Your username or org (myuser/myapp)
Rate limits       100 pulls/6h unauthenticated — log in in CI
```

## Related

- [Image commands reference](../02-commands/image-commands.md) — full push/pull/tag command reference
- [Image layers guide](./image-layers.md) — how layers are transferred during pull
- [Dockerfile reference](./dockerfile-reference.md) — building images to push
- [DevOps roadmap](./devops-roadmap.md) — where registry fits in CI/CD pipelines
