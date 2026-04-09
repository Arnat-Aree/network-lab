# 🌐 Enterprise Network & Microservices Emulation Lab
**Computer Networks & Microservices Architecture Core Project**

[![Platform Architecture](https://img.shields.io/badge/Architecture-Docker%20Native%20L3%2FL4-blue?style=for-the-badge&logo=docker)](https://docker.com)
[![Routing Engine](https://img.shields.io/badge/Routing-FRRouting%20(OSPF)-red?style=for-the-badge)](https://frrouting.org)
[![Security Layer](https://img.shields.io/badge/Security-StrongSwan%20%2B%20iptables-black?style=for-the-badge)](https://strongswan.org)
[![Tested With](https://img.shields.io/badge/Tested_With-Python%20T--800%20Suite-green?style=for-the-badge&logo=python)](scripts/)

> **A Next-Generation Hardware Emulation Approach:**
> This repository houses the complete transition from static Cisco Packet Tracer simulations towards **Cloud-Native Virtualization**. We engineer custom Alpine Linux containers to directly modify Linux Kernel Forwarding Information Bases (FIB), establishing actual VPN tunnels, dynamic OSFP route calculations, and hardware failovers inside a localized environment.

---

## 🏛️ Repository Architecture

This mono-repo is structurally divided into sophisticated lab scenarios, each progressively adding extreme layers of Enterprise Network capabilities. 

| Phase | Deployment | Technical Scope | Status | Validation Metric |
|-------|------------|-----------------|--------|-------------------|
| **[Lab 6](./lab6/)** | `docker-compose up` | **Resilient Intranets:** Single ISP Gateway, OSPF Internal Areas, Dynamic IP SLA Failovers, Web App Exposure, and Kernel `iptables` NAT masking. | 🟢 **Verified** | Automated Suite |
| **[Lab 7](./lab7/)** | `docker-compose up` | **Dual-Site Data Center:** Multi-WAN (Dual ISPs), Hardware Gateway Redundancy via **VRRP**, Branch Cryptographic Tunnels via **IPsec IKEv2**, App Load Balancing (Nginx), and Grafana NOC Logging. | 🟢 **Verified** | **24/24 PASS (CI/CD)** |

*(Click on the Lab links above for deep-dive technical engineering reports, topological diagrams, and animated proofs of concept).*

---

## 🚀 Global Quick Start

It is highly recommended to execute these labs on a host running Docker Engine or Docker Desktop with at least 4GB of allocated RAM.

```bash
# 1. Clone the master repository
git clone https://github.com/Arnat-Aree/network-lab.git
cd network-lab

# 2. Enter the desired lab dimension (e.g., Lab 7)
cd lab7

# 3. Spin up the entire multi-subnet topology
docker-compose up -d --build

# 4. Await Routing Convergence (~30 seconds)
# Let Daemon routers (zebra) elect their active Masters and negotiate Cryptographic Keys.

# 5. Trigger the rigorous python verification engines!
python3 scripts/test_resiliency.py
```

---

## 🛠️ Technological Stack

We utilize a modern DevOps strategy bridging native networking protocols with observable microservices.

- **Infrastructure:** Docker Compose (Automated container deployment over isolated subnets).
- **Core Networking:** 
  - `FRRouting (FRR)` for OSPF dynamic path discoveries.
  - `Keepalived` for VRRP hardware IP migration.
  - `StrongSwan` for Military-grade IPsec IKEv2 Site-to-Site Encapsulation.
- **Application & Load Balancing:** `Nginx` (Round Robin / Proxy), `Node.js / Express`, `PostgreSQL`, `Redis` (In-Memory caching).
- **Automation & CI/CD:** Native Bash Scripts, Python `requests/docker` APIs for deep environment unit-testing, bridged into **GitHub Actions** workflows.
- **Observability:** `Rsyslog` streaming to `Grafana`, `Loki`, and `Promtail`.

---

## 👥 Meet the Network Engineering Team

This sophisticated infrastructure was architected, coded, and valiantly maintained by:

| Student ID | Engineer / Developer |
|:---:|---|
| **673380411-3** | นายปฏิกาณ ปานทะเล |
| **673380413-9** | นายปิยพันธ์ แก้วเก็บคำ |
| **673380426-0** | นายวรปรัชญ์ พิมพ์อุบล |
| **673380432-5** | นายอาณัฐ อารีย์ |
| **673380434-1** | นายเนติภัทร ภูครองเพชร |
| **673380582-6** | นายณัฐชา อรรคอาต |
| **673380599-9** | นายรัชชานนท์ ประดับแก้ว |

---
*University of Khon Kaen — Department of Computer Science*
