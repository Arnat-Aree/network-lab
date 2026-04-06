# 🌐 Lab 7: Enterprise Data Center Architecture & Observability

> **Course:** Computer Networks & Microservices Architecture  
> **Topic:** True Hardware Emulation with FRRouting, IPsec, and Observability  
> **Status:** ✅ Completed (Pass Rate: 100%)

---

## 🚀 Enterprise Standard Architecture
This topology **faithfully emulates a physical Enterprise Wide Area Network (WAN)**. 
We implemented **Layer 3 & Layer 4 protocols** natively using Alpine containers acting as physical routers. This includes **Dynamic Routing (OSPF)**, **High-Availability Gateways (VRRP)**, and **Military-Grade Encryption (IPsec)**.

To marry the core network with modern DevSecOps standards, we successfully infused **Nginx Reverse Proxy Load Balancing** across a Demilitarized Zone (DMZ), stateful **Database/Cache layers**, and a pristine **Grafana + Loki Observability Stack**.

---

## 🗺️ Physical-Level Network Topology

```text
       [ ISP 1 (172.30.1.0/24) ]                 [ ISP 2 (172.30.2.0/24) ]
                   │                                         │
                   └───────────────────┬─────────────────────┘
                                       │
  ╔════════════════════════════════════▼════════════════════════════════════╗
  ║                        EXTERNAL WAN BOUNDARY                            ║
  ╚═════════════════════════════════╤════╤══════════════════════════════════╝
    [ IPsec IKEv2 TUNNEL ] ---------│    │--------- [ IPsec IKEv2 TUNNEL ]
                                    │    │
            ┌───────────────────────┴────┴───────────────────────┐
            │                     VRRP VIP                       │
            │                  [172.20.10.1]                     │
            │                  [172.20.30.1]                     │
            │        ┌──────────────┐    ┌──────────────┐        │
            │        │   Router 1   │    │   Router 3   │        │
            │        │ (VRRP Pri:200)    │ (VRRP Pri:100)        │
            │        └──────┬───────┘    └──────┬───────┘        │
            └───────────────┼───────────────────┼────────────────┘
                            │                   │
             ┌──────────────┴───────────────────┴─────────────┐
             │               DMZ ZONE (172.20.30.0/24)        │
             │           ┌────────────────────────┐           │
             │           │  NGINX LoadBalancer    │           │
             │           │  Port 80 (Round Robin) │           │
             │           └──────────┬─────────────┘           │
             └──────────────────────┼─────────────────────────┘
                                    │
                                    ├───► [ ServerA-1 (Node 1) ]
                                    ├───► [ ServerA-2 (Node 2) ]
                                    │
             ┌──────────────────────┴─────────────────────────┐
             │       CORE LAN (HQ: 172.20.10.0/24)            │
             │ ┌─────────────┐ ┌──────────┐ ┌───────────────┐ │
             │ │ PostgreSQL  │ │  Redis   │ │ Syslog/Loki   │ │
             │ │ (10.12)     │ │ (10.11)  │ │ (10.100, 41)  │ │
             │ └─────────────┘ └──────────┘ └───────┬───────┘ │
             └──────────────────────────────────────┼─────────┘
                                                    │
                                                    ▼
                                          [ GRAFANA (Port: 3000) ]
```

---

## 🛠️ Feature Breakdown

### 1. 🛡️ Core Infrastructure & Routing (The Network Layer)
| Feature | Implementation | Description |
|---------|----------------|-------------|
| **Dual ISP Redundancy** | Physical separation | Traffic can route out natively through 2 ISPs avoiding single point of failure |
| **VRRP Failover Gateway** | `FRRouting / vrrpd` | R1 (Master) drops? R3 (Backup) instantly acquires the `.1` Virtual IP. **(Zero Downtime)** |
| **IPsec StrongSwan** | `IKEv2 / AES-256` | Encrypts `172.20.10.0/24` $\leftrightarrow$ `172.20.20.0/24` cleanly bypassing the plaintext ISPs. |
| **Stateful Firewall NAT** | `iptables` | Strict `DNAT` for exposed LoadBalancer, `MASQUERADE` for outbound internet. |

### 2. 💻 Application & Data Tier (The Software Layer)
| Feature | Implementation | Description |
|---------|----------------|-------------|
| **Microservice Load Balancing** | Nginx Reverse Proxy | Proxies port 80 traffic implicitly into `ServerA-1` and `ServerA-2` via round-robin. |
| **Stateful Persistence** | PostgreSQL 15 | Relational transactions mapped automatically into persistent Docker volumes. |
| **In-Memory Caching**| Redis 7 | Accelerates endpoint requests while demonstrating service decoupling. |

### 3. 🎯 Observability & Automation (The Management Layer)
| Feature | Implementation | Description |
|---------|----------------|-------------|
| **Automated Verification** | `test_resiliency.py` | Python Script auto-simulating ping tests, IPsec verifications, and LoadBalancer distributions. |
| **Centralized Protocol Logs** | `rsyslog` $\rightarrow$ `Promtail` | Routers generate native OS logs (OSPF/VRRP transitions) into a central Linux socket. |
| **Dashboard Analytics** | Grafana + Loki | Visualizes network convergence metrics and syslogs via `http://localhost:3000`. |

---

## 🧪 One-Click Test Automation

Forget manual `curl` sequences. We built a native **Resiliency Automation Script** that runs live checks against the entire topology.

```bash
# Execute the network test pipeline
python3 scripts/test_resiliency.py
```

### 📋 Expected Result Output
```text
  ╔══════════════════════════════════════════════════╗
  ║   Lab 7 — Network Engineering Validation Suite   ║
  ║   Automated Topology Verification Script         ║
  ╚══════════════════════════════════════════════════╝

  ✅ PASS  Container R1 running
  ✅ PASS  Traffic distributed to 2+ nodes  -->  {'Srv2': 5, 'Srv1': 5}
  ✅ PASS  IPsec SA Established (R1 tunnel bounds with R2)
```

---

## 🌐 Quick Deploy

```bash
# 1. Bring up the Enterprise network
docker-compose up -d --build

# 2. View Real-time Grafana Logs (Login: admin / admin)
Open Browser: http://localhost:3000

# 3. Simulate Router Failure (Watch OSPF/VRRP converge on Grafana!)
docker stop R1
```
