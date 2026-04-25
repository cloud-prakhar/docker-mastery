# Networking Deep Dive

## How Bridge Networking Works

When Docker creates a bridge network, it:
1. Creates a virtual bridge interface on the host (e.g., `docker0` or `br-<id>`)
2. Assigns a subnet (e.g., `172.17.0.0/16`)
3. For each container, creates a **veth pair** — one end in the container's network namespace (`eth0`), one end on the bridge
4. The bridge routes traffic between containers and to the host via iptables NAT rules

```
Host
├── docker0 (bridge: 172.17.0.1)
│   ├── veth0a  ──────►  Container A (172.17.0.2 eth0)
│   └── veth0b  ──────►  Container B (172.17.0.3 eth0)
│
└── iptables NAT: container traffic → host IP for outbound internet
```

Inspect with:
```bash
ip addr show docker0
ip link show
iptables -t nat -L DOCKER
```

## Embedded DNS

User-defined networks get an embedded DNS resolver at `127.0.0.11:53` inside each container. This resolver answers queries for other containers on the same network.

```bash
# Inside a container
cat /etc/resolv.conf
# nameserver 127.0.0.11
# options ndots:0

nslookup db           # resolves to db container's IP
nslookup db.mynet     # FQDN form
```

## Host Networking

```bash
docker run --network host nginx
```

The container shares the host's network stack — `nginx` listens on the host's port 80 directly. No NAT, lowest latency.

Not available on Docker Desktop (macOS/Windows) — the "host" in that context is the Linux VM, not your Mac/Windows machine.

## None Network

```bash
docker run --network none alpine ping 8.8.8.8
# PING: Network unreachable
```

Useful for batch jobs that must not touch the network.

## Connecting a Container to Multiple Networks

```bash
docker network create frontend
docker network create backend

docker run -d --name app --network frontend myapp
docker network connect backend app
# app is now reachable on both networks
```

## Network Troubleshooting

```bash
# Inspect network and see which containers are attached
docker network inspect app-net

# Check container's IP and network config
docker inspect -f '{{json .NetworkSettings.Networks}}' CONTAINER | jq

# Test connectivity between containers
docker exec container-a ping container-b
docker exec container-a curl http://container-b:8080/health

# Use a debug container with network tools
docker run --rm -it --network app-net nicolaka/netshoot sh
# inside: dig, nslookup, curl, nmap, tcpdump, ss, etc.
```

## DNS Round-Robin (Poor-Man Load Balancing)

```bash
docker network create lb-net

# Start 3 instances with the same network alias
docker run -d --name app1 --network lb-net --network-alias app myapp
docker run -d --name app2 --network lb-net --network-alias app myapp
docker run -d --name app3 --network lb-net --network-alias app myapp

# DNS returns all 3 IPs for "app" — clients round-robin
docker run --rm --network lb-net alpine nslookup app
```

## Overlay Networks (Swarm / Multi-Host)

Overlay networks span multiple Docker hosts using VXLAN encapsulation. They require Docker Swarm mode to be initialized.

```bash
docker swarm init
docker network create --driver overlay --attachable my-overlay
```

Containers on different hosts can communicate as if on the same LAN — Docker handles the tunneling transparently.
