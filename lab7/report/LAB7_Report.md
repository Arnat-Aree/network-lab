# Lab 7: Data Center Infrastructure Report

## 1. Objective
To design and implement an Enterprise-grade Data Center architecture incorporating Gateway Redundancy (VRRP), Site-to-Site VPN (IPsec), Demilitarized Zone (DMZ), Load Balancing, and layered Database architectures.

## 2. Infrastructure Topology
- **ISP 1 & 2 Clouds**: Represents external wide-area routing via `172.30.1.0/24` and `172.30.2.0/24`.
- **HQ Gateway (R1 & R3)**: Active-backup setup providing load distribution to the DMZ and internal core.
- **DMZ Zone**: Houses NGINX LoadBalancer and Python application instances exposed safely via port 80 forwarding.
- **HQ LAN A**: Houses internal databases (PostgreSQL & Redis) and logging servers which are fully isolated from the internet.
- **Branch LAN B**: Connected via secure IPsec tunnel through R2.

## 3. Key Components
### Site-to-Site VPN
StrongSwan `ipsec.conf` was established to encrypt subnets `172.20.10.0/24` (HQ) and `172.20.20.0/24` (Branch) over the public `172.30.1.0/24` intermediary network.

### Microservice Interaction
Application servers (`ServerA-1`, `ServerA-2`) respond to HTTP events by incrementing a hits counter in **Redis** and committing a transaction log to **PostgreSQL**. The responses natively return these calculated counts demonstrating functional persistence.

### High Availability
The FRRouting `vrrp` daemon monitors logical states within the `lan_a` and `dmz` interfaces. Manual fallbacks using `ip addr add` are automated to immediately ensure service uptime.

## 4. Verification Checklists
- [x] OSPF neighbors converge.
- [x] IPsec tunnels establish IKEv2 connection.
- [x] NGINX forwards traffic utilizing Round-Robin matching across `ServerA-X`.
- [x] Docker environments segregate services functionally into specific broadcast domains.

## 5. Result Validation
### 5.1 IPsec Tunnel Status (HQ Edge Router 1)
```console
# docker exec R1 ipsec status
Security Associations (2 up, 0 connecting):
      branch[2]: ESTABLISHED 50 minutes ago, 172.30.1.1[172.30.1.1]...172.30.1.2[172.30.1.2]
      branch{3}:  INSTALLED, TUNNEL, reqid 1, ESP SPIs: cc6a1664_i c83e457a_o
      branch{3}:   172.20.10.0/24 172.20.30.0/24 === 172.20.20.0/24
      branch[1]: ESTABLISHED 50 minutes ago, 172.30.1.1[172.30.1.1]...172.30.1.2[172.30.1.2]
      branch{4}:  INSTALLED, TUNNEL, reqid 1, ESP SPIs: cc717dd7_i c3b78931_o
      branch{4}:   172.20.10.0/24 172.20.30.0/24 === 172.20.20.0/24
```
The IPsec log confirms the SA association established successfully, securely linking the 3 critical subnets `172.20.10.0/24`, `172.20.30.0/24`, and `172.20.20.0/24` over the simulated unsecure transit `172.30.1.0/24`.
