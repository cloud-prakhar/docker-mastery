# Docker in the DevOps Roadmap

> This guide shows exactly where Docker fits in the broader DevOps skill set and how mastering it accelerates a role switch.

---

## What is DevOps?

DevOps is the practice of **closing the gap between development (writing code) and operations (running code in production)**. Instead of developers throwing code over the wall to ops, both sides share tools, processes, and responsibility.

```
Traditional (Siloed):

  Developer          Wall          Ops Team
  ─────────          ────          ────────
  writes code   →  "here ya go"  → figures out
  locally                           deployment
  (months pass)                   (fires everywhere)


DevOps (Collaborative):

  Developer  +  Ops  =  DevOps Engineer
  ─────────────────────────────────────
  writes code with deployment in mind
  builds CI/CD pipelines
  monitors production themselves
  uses infrastructure as code
  (deploys multiple times per day)
```

---

## The DevOps Roadmap — Where Docker Fits

```
STAGE 1: FOUNDATIONS
┌─────────────────────────────────────────────────────┐
│  Linux basics          → file system, processes,    │
│                           systemd, ssh, permissions │
│  Networking basics     → TCP/IP, DNS, HTTP, ports   │
│  Git                   → branching, PRs, conflicts  │
│  Shell scripting       → bash, pipes, cron          │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
STAGE 2: CONTAINERS  ◄─── YOU ARE HERE
┌─────────────────────────────────────────────────────┐
│  ★ Docker              → images, containers,        │
│                           Dockerfile, volumes,      │
│                           networking, Compose       │
│  Container concepts    → namespaces, cgroups,       │
│                           image layers, registries  │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
STAGE 3: CI/CD
┌─────────────────────────────────────────────────────┐
│  GitHub Actions        → build, test, push image    │
│  Jenkins / GitLab CI   → pipelines, agents          │
│  Docker in CI          → docker build in pipelines  │
│  Image scanning        → Trivy, Snyk for CVEs       │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
STAGE 4: ORCHESTRATION
┌─────────────────────────────────────────────────────┐
│  Kubernetes (K8s)      → pods, deployments,         │
│                           services, ingress,        │
│                           ConfigMaps, Secrets       │
│  Helm                  → K8s package manager        │
│  Docker Swarm          → simpler alternative to K8s │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
STAGE 5: CLOUD
┌─────────────────────────────────────────────────────┐
│  AWS / GCP / Azure     → EC2, ECS, EKS, GKE, AKS   │
│  Container registries  → ECR, GCR, ACR              │
│  Managed K8s           → EKS, GKE, AKS              │
│  Serverless containers → AWS Fargate, Cloud Run     │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
STAGE 6: INFRASTRUCTURE AS CODE
┌─────────────────────────────────────────────────────┐
│  Terraform             → provision VMs, networks,   │
│                           managed services          │
│  Ansible               → configure servers          │
│  Pulumi                → IaC in real languages      │
└─────────────────────────────────────────────────────┘
                          │
                          ▼
STAGE 7: OBSERVABILITY
┌─────────────────────────────────────────────────────┐
│  Prometheus + Grafana  → metrics and dashboards     │
│  ELK / Loki            → log aggregation            │
│  Jaeger / Tempo        → distributed tracing        │
│  Alerting              → PagerDuty, OpsGenie        │
└─────────────────────────────────────────────────────┘
```

---

## Why Docker is the Best Starting Point

Docker sits at **Stage 2**, but it unlocks everything after it:

```
Without Docker knowledge, you cannot:

  CI/CD     → "build the Docker image" is step 1 in every pipeline
  K8s       → Kubernetes runs containers; you must know images/Compose first
  Cloud     → ECS, EKS, Cloud Run, Fargate all run Docker containers
  IaC       → Terraform modules often provision container infrastructure
  Monitoring → container metrics (CPU, memory per container) are fundamental
```

Docker is the **lingua franca of modern infrastructure**. Every DevOps tool assumes you understand it.

---

## Docker Skills → DevOps Job Tasks (Direct Mapping)

| Docker Skill You Learn Here | Real DevOps Job Task |
|---|---|
| Writing Dockerfiles | Containerizing legacy apps for cloud migration |
| Multi-stage builds | Optimizing CI build times and image sizes |
| Docker Compose | Setting up local dev environments for teams |
| Health checks | Defining readiness/liveness probes in Kubernetes |
| Named volumes | Designing stateful service persistence strategies |
| Networking / DNS | Debugging microservice communication failures |
| Pushing to registry | Publishing artifacts in a CI/CD pipeline |
| `docker logs`, `docker exec` | Debugging production container incidents |
| Image scanning | Implementing security gates in pipelines |
| `.env` + override files | Managing config across dev/staging/prod |

---

## The Docker → Kubernetes Bridge

The concepts you learn in Docker map almost 1:1 to Kubernetes:

```
Docker Concept          Kubernetes Equivalent
──────────────────────────────────────────────────────
Container               Container (inside a Pod)
docker run              Pod spec
docker-compose.yml      Deployment YAML
--restart always        restartPolicy: Always
-p 8080:80              Service (NodePort/LoadBalancer)
Named volume            PersistentVolumeClaim (PVC)
docker network          Service DNS + NetworkPolicy
--env / env_file        ConfigMap / Secret
healthcheck             livenessProbe / readinessProbe
docker build + push     CI step: docker build, docker push
```

Once you internalize Docker Compose, reading a Kubernetes manifest feels familiar — it's the same mental model with more power and more complexity.

---

## Realistic 90-Day Docker → DevOps Transition

```
Week 1-2   │  This repo: basics, Dockerfile, images, containers
Week 3-4   │  This repo: Compose, volumes, networking, projects
Week 5-6   │  GitHub Actions: build + test + push Docker image
Week 7-8   │  Kubernetes: pods, deployments, services (minikube locally)
Week 9-10  │  Cloud: deploy a container to AWS ECS or GCP Cloud Run
Week 11-12 │  Polish: Helm chart, Prometheus metrics, write your own runbook
```

At week 12 you have: a containerized app, a CI/CD pipeline, a K8s deployment, and a cloud-deployed service — a complete portfolio project.

---

## What This Repo Covers on the Roadmap

```
DevOps Roadmap
│
├── [✓] Containers & Docker
│        ├── [✓] 01-basics      → concepts, Dockerfile, hypervisors
│        ├── [✓] 02-commands    → full CLI reference
│        ├── [✓] 03-compose     → multi-container orchestration
│        ├── [✓] 04-volumes     → data persistence patterns
│        ├── [✓] 05-networking  → bridge, DNS, overlay
│        └── [✓] 06-projects    → real stacks to put in your portfolio
│
├── [ ] CI/CD with Docker        → next step after this repo
├── [ ] Kubernetes               → after CI/CD
├── [ ] Cloud (ECS / GKE)        → parallel to K8s
└── [ ] IaC, Monitoring          → after cloud fundamentals
```

The checkbox that matters most right now is **Containers & Docker** — and this repo is designed to tick every item in it.
