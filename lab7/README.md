# 🖧 Lab 7 — Enterprise Data Center Architecture & L3/L4 Network Engineering

> **Course:** Computer Networks & Microservices Architecture  
> **Replaces:** Cisco Packet Tracer / Physical Infrastructure Setup  
> **Execution Platform:** Docker-Based Deep Kernel Networking (Alpine + FRR + StrongSwan)  
> **Status:** 🟢 100% Automated CI/CD Passing / Production Ready

[![CI/CD Validated](https://img.shields.io/badge/CI%2FCD-100%25%20Passing-success?style=for-the-badge&logo=githubactions)](.github/workflows/lab7-ci.yml)
[![FRRouting](https://img.shields.io/badge/FRRouting-OSPF%20Area%200-blue?style=for-the-badge)](config/)
[![Keepalived](https://img.shields.io/badge/Keepalived-VRRP%20HA-red?style=for-the-badge)](automation/)
[![StrongSwan](https://img.shields.io/badge/StrongSwan-IPsec%20VPN-black?style=for-the-badge)](automation/)
[![Grafana](https://img.shields.io/badge/Grafana-NOC%20Dashboard-orange?style=for-the-badge)](automation/Observability)

---

## 🗺️ Network Topology (L3/L4 Infrastructure Emulation)

Unlike pure application-layer bridging, this topology utilizes **Alpine Linux routers modifying kernel Forwarding Information Bases (FIB)** to perform true dynamic routing, failover, and cryptographic tunneling.

```text
                             [ ISP 1 & ISP 2 Clouds ]
                       (Untrusted Public WANs: 172.30.1.0/24 & 172.30.2.0/24)
                                           │
                                           ▼
           ╔════════════════════════════════════════════════════════════════╗
           ║            IPsec IKEv2 SITE-TO-SITE ENCRYPTED TUNNEL           ║
           ║             [ AES-256-CBC | SHA-256 | ESP Payload ]            ║
           ╚════════════════════════════════════════════════════════════════╝
                 │                                                  │
    ┌────────────┴─────────────┐                       ┌────────────┴─────────────┐
    │     [ Headquarters ]     │                       │     [ Branch Office ]    │
    │  Dual WAN / Failover HA  │                       │      Remote Network      │
    │  R1 (Master)  R3 (Backup)│                       │           R2             │
    │  VRRP Pri:200 VRRP Pri:10│                       │    172.20.20.254 (LAN)   │
    └────────────┬─────────────┘                       └────────────┬─────────────┘
                 │ (VIP: 172.20.30.1)                               │ 
    ┌────────────┴─────────────┐                       ┌────────────┴─────────────┐
    │      DMZ RESTRICTED      │                       │         LAN B            │
    │      172.20.30.0/24      │                       │     172.20.20.0/24       │
    │                          │                       │                          │
    │ [ NGINX LoadBalancer ]   │<-- Load Balances      │     [ ServerB ]          │
    │ [ ServerA-1 (Node 1) ]   │    to App Tier        │     [ ClientA ]          │
    │ [ ServerA-2 (Node 2) ]   │                       │      (VPN Tester)        │
    └────────────┬─────────────┘                       └──────────────────────────┘
                 │ (VIP: 172.20.10.1)
    ┌────────────┴─────────────┐
    │    CORE PROTECTED LAN    │
    │      172.20.10.0/24      │
    │                          │
    │ [ PostgreSQL 15 ] (DB)   │ 
    │ [ Redis 7 ] (Cache)      │
    │ [ Syslog / Promtail ]    │ --> Streams live kernel network logs to Grafana
    │ [ Grafana Dashboard ]    │
    └──────────────────────────┘
```

---

## 🏗️ Enterprise Architecture Highlights

| Design Paradigm | Packet Tracer Concept | Our Docker Execution |
|---|---|---|
| **Dynamic Discovery** | OSPF Routing | **FRRouting (FRR):** Runs `zebra` & `ospfd` modifying Linux kernel tables. |
| **High Availability Gateway** | HSRP / VRRP | **Keepalived:** Native VRRP elections floating IPs via physical MAC mapping. |
| **Encrypted Wan Tunneling** | IPsec VPN | **StrongSwan:** Negotiating IKEv2 keys & wrapping traffic in ESP payloads. |
| **Stateful Edge Protection** | Cisco ASA / ACL | **iptables:** Deep PREROUTING DNAT & symmetrical MASQUERADE SNAT. |
| **NOC Operations**| Syslog Server | **Loki + Promtail + Grafana:** C-level networking logs piped into beautiful UIs. |

---

## 📁 Project Structure

```text
network-lab/lab7/
├── 📄 docker-compose.yml             ← Orchestrates all 15 nodes / subnets
├── 📄 README.md
│
├── 📂 automation/                    ← Service Blueprints & Daemons
│   ├── ClientA/                      ← Simulates LAN B workstation (Ping Tester)
│   ├── LoadBalancer/                 ← Nginx Upstream Config (Round-Robin)
│   ├── Observability/                ← Dashboards (Grafana) & Pipe configs (Loki)
│   ├── R1/                           ← Primary Gateway (VPN Term + FW + OSPF)
│   ├── R2/                           ← Branch Router (VPN Return)
│   ├── R3/                           ← Secondary Gateway (VRRP Backup)
│   ├── ServerA/                      ← HQ API App Tier (connects to DB)
│   ├── ServerB/                      ← Branch HTTP Target
│   └── Syslog/                       ← Aggregates UDP logs from router components
│
├── 📂 config/                        ← Immutable Runtime Overlays
│   └── R{1,2,3}/frr.conf             ← Dynamic Interface Detection + Network Advertisements
│
├── 📂 scripts/                       ← DevOps Tooling
│   ├── test_resiliency.py            ← 🤖 24-point Headless Test Suite 
│   └── demo_failover.sh              ← Live terminal presentation script
│
└── 📂 report/                        
    └── LAB7_Report.md                ← Deep Engineering Whitepaper
```

---

## 🚀 Quick Start Deployment

### Prerequisites
- Docker Engine & `docker-compose`
- Python 3.x (to execute the validation suite)

### 1. Build and Subnet Initialization
```bash
docker compose up -d --build
```
> ⚠️ **CPU Soak Time Recommended:** Wait exactly 30 seconds post-boot. The L3 routers (`zebra`, `ospfd`) must calculate network adjacencies and `StrongSwan` must negotiate IKEv2 encryption keys before cross-site traffic can flow. 

### 2. Verify Initial Container State
```bash
docker compose ps
# Expected: All 15 containers Up and Running
```

---

## 📺 Live Operational View (NOC Dashboard)

The Enterprise Network is entirely visualized using a customized Grafana frontend. The observability stack (`Loki`/`Promtail`) intercepts raw hardware syslogs (IKEv2 handshakes, OSPF state drops) and streams them into this centralized monitoring interface.

![Grafana NOC Live Demo](assets/grafana_demo.webp)

| Service Endpoint | Target Output |
|------------------|---------------|
| `http://localhost:80/` | Hits the DMZ LoadBalancer; API proxies down to ServerA tier (Round Robin). |
| `http://localhost:3000/`| **Grafana Dashboard** (Login: `admin` / `admin`). Watch Live OSPF/IPsec Metrics. |

---

## ⚡ Live Hardware Failover Demo

We prove true network HA (High Availability) by "pulling the plug" on the Primary Router (R1) and observing VRRP dynamically shifting the IP to the Backup Router (R3) without dropping application connections.

```bash
# Execute the live presentation script
bash scripts/demo_failover.sh
```

**What happens inside the kernel?**
```text
[HQ Client] Ping 172.20.10.1 (Gateway) ... Reply from 172.20.10.2 (R1 MAC)
# --- docker stop R1 ---
[R3 VRRP Daemon] Status transitioned to MASTER (Priority 100)
[HQ Client] Ping 172.20.10.1 (Gateway) ... Reply from 172.20.10.3 (R3 MAC)
```

---

## 🔁 Enterprise CI/CD Pipeline & Protection

This lab includes a rigorous **GitHub Actions CI/CD Pipeline** (`.github/workflows/lab7-ci.yml`) acting as a DevOps guardrail. It prevents any configuration "drift" from breaking network routing.

- **Trigger:** Automatic on code pushes to `main`.
- **Mechanism:**
  1. Spawns headless Azure Ubuntu instances.
  2. Binds configuration arrays using `frr_template` overlays (to prevent Git File Mutation bugs).
  3. Pauses for exactly 30s allowing Kernel OSPF recalculations.
  4. Triggers the **T-800 Resiliency Validation Script** internally.
- **Fail-Fast Notification:** If a ping or IPsec tunnel fails, GitHub renders the failure natively into the pull request UI!

---

## 🧪 The "T-800" Automated Resiliency Suite

Instead of manual `ping` tests, we orchestrate a massive Python verifier that systematically inspects Linux Kernel Routing Tables, Cryptographic ESP States, and API Caches.

```bash
# Run the verification engine
python3 scripts/test_resiliency.py
```

### Excerpt of Output Matrix
```text
██████████████████████████████████████████████████████████████████████
         █   LAB 7 - ENTERPRISE DATA CENTER VALIDATION SUITE          
            █   Automated Protocol & Service Verification             
██████████████████████████████████████████████████████████████████████

  PHASE 1: INFRASTRUCTURE & CONNECTIVITY
 [R-01] ✅ PASS | Node R1 Health
 [R-09] ✅ PASS | Branch WAN Reachability

  PHASE 2: DYNAMIC ROUTING & HIGH AVAILABILITY
 [O-10] ✅ PASS | OSPF Area 0 Adjacencies
 [O-11] ✅ PASS | Route Synchronization
 [V-12] ✅ PASS | VRRP: R1 Master Election (VIP bound to eth2)

  PHASE 3: SECURITY, FAILOVER & PERSISTENCE
 [S-16] ✅ PASS | IPsec Site-to-Site Tunnel ESTABLISHED
 [S-17] ✅ PASS | IPsec ESP Encryption (XFRM state active)
 [M-21] ✅ PASS | Load Balancing Fair Distribution

  PHASE 4: FIREWALL & OBSERVABILITY
 [F-22] ✅ PASS | Firewall Stateful Rules (iptables)
 [L-23] ✅ PASS | Syslog Aggregation Active (rsyslogd)
 [L-25] ✅ PASS | NOC GUI: Grafana Dashboard

══════════════════════════════════════════════════════════════════════
               ✅ FINAL STATUS: 24/24 PASS — 100% SUCCESS              
══════════════════════════════════════════════════════════════════════
```

---

## 🛑 Stop & Cleanup Operations

Data persistence exists via Docker Volumes (for PostgreSQL, Loki, etc). 

```bash
# Graceful Stop (preserves DB data & Loki logs)
docker-compose down

# Total Destructive Wipe (Resets everything to zero)
docker-compose down -v --remove-orphans
```

---
*Developed under extreme stress conditions to enforce modern Site Reliability Engineering standards.*
