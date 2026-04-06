# 🖧 Lab 7 — Enterprise Data Center Architecture & Observability

> **Course:** Computer Networks & Microservices Architecture  
> **Lab Focus:** Network Infrastructure (L3/L4) with Application Delivery (L7)  
> **Status:** ✅ Completed (Pass Rate: 100%)  

[![Docker Compose](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)](#) 
[![FRRouting](https://img.shields.io/badge/Router-FRRouting-orange)](#) 
[![IPsec](https://img.shields.io/badge/Security-StrongSwan-green)](#) 
[![Grafana](https://img.shields.io/badge/Observability-Grafana_Loki-orange)](#) 
[![Test](https://img.shields.io/badge/Test-Automated-success)](#)

---

## 🚀 About This Lab

This lab replaces traditional Cisco Packet Tracer simulations with **native Docker container emulation**. We engineered a physical-grade Network Architecture focusing tightly on core routing, edge security, and failover capabilities. 

Key implementations include:
- **High-Availability Gateway (VRRP):** Master/Backup edge routers for zero-downtime ISP failures.
- **Dynamic Routing (OSPF):** Handled via `zebra` and `ospfd` modifying underlying Linux Kernel FIBs.
- **Secure Encrypted Tunneling:** IPsec (IKEv2) protecting inter-office subnets.
- **Observability:** Centralized Syslogs aggregated into Grafana/Loki.

> 📖 **Read the full engineering blueprint and test results in our [Complete Lab Report](report/LAB7_Report.md).**

---

## 🗺️ High-Level Network Topology

```text
               [ ISP 1 & ISP 2 ] (Untrusted WAN)
                       │
       ╔═══════════════▼════════════════════════════════════╗
       ║        IPsec IKEv2 SITE-TO-SITE ENCRYPTION         ║
       ╚═══════════════╤════════════════════════════════════╝
                       │      
    [ Headquarters (HQ) ]                 [ Branch Office ]
     R1 (Master)  R3 (Backup)                   R2
     VIP 172.20.X.1                       172.20.20.254
                       │
            ┌──────────┴─────────┐
            │      DMZ ZONE      │
            │ [ Nginx Proxy ]    │ --> Round-robin Load Balancer
            │ [ Node.js APIs ]   │ 
            └──────────┬─────────┘
                       │
            ┌──────────┴─────────┐
            │     CORE LAN       │
            │ [ PostgreSQL ]     │ --> Stateful Database
            │ [ Redis Cache ]    │
            │ [ Grafana/Loki ]   │ --> Observability Stack
            └────────────────────┘
```

---

## ⚡ Quick Start Deployment

### 1. Initialize the Enterprise Network
Clone this repository and spin up the Docker-compose environment.
```bash
docker-compose up -d --build
```
*Wait 10-15 seconds for OSPF dynamic neighbor discovery to stabilize.*

### 2. Run the Validation Suite
This suite tests Network Availability, Nginx load distributions, and StrongSwan IPsec VPN Tunnel integrity automatically.
```bash
python3 scripts/test_resiliency.py
```

### 3. Open the Observability Dashboard
Navigate to our pre-provisioned Network Logs Portal:
- **URL:** [http://localhost:3000](http://localhost:3000)
- **Login:** `admin` / `admin`

---

## 📁 System Architecture Organization

```text
network-lab/lab7/
├── 📄 docker-compose.yml          # Core Infrastructure Builder
├── 📂 automation/                 # Dockerfiles and Container Logic
│   ├── 📂 LoadBalancer/           # Nginx Configuration
│   ├── 📂 Observability/          # Promtail, Loki, and Grafana Dashboard
│   ├── 📂 R1/                     # Master VRRP, OSPF, ipsec configs
│   └── 📂 Syslog/                 # Syslog Forwarder (Rsyslog)
│
├── 📂 config/                     # Routing engine injections (FRR)
├── 📂 scripts/                    # Automation and Validation Tools
└── 📂 report/                     # The Complete Engineering Report
    └── 📄 LAB7_Report.md          # 25+ automated test validations
```

---

## 🛑 Cleanup & Teardown

To shut down the internal ISP routes and tear down the data center:
```bash
docker-compose down
```
*(To completely wipe all relational databases and logs, utilize `docker-compose down -v`)*
