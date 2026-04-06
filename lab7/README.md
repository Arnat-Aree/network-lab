# 🖧 Lab 7 — Enterprise Data Center & Network Engineering Validation

> **Course:** Computer Networks & Microservices Architecture  
> **Replaces:** Cisco Packet Tracer / Physical Router Topology Configuration  
> **Execution Platform:** Docker-based L3/L4 Infrastructure Emulation  

---

## 🗺️ Network Topology (L3/L4 Emulation)

Unlike pure application-layer bridging, this topology utilizes **Alpine Linux routers modifying kernel Forwarding Information Bases (FIB)** to perform true routing (OSPF, VRRP) and cryptographic tunneling (IPsec).

```text
                             [ ISP 1 & ISP 2 Clouds ]
                       (Untrusted Public WAN: 172.30.1.0/24)
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
                 │ (172.20.30.1)                                    │ 
    ┌────────────┴─────────────┐                       ┌────────────┴─────────────┐
    │      DMZ RESTRICTED      │                       │         LAN B            │
    │      172.20.30.0/24      │                       │     172.20.20.0/24       │
    │                          │                       │                          │
    │ [ NGINX LoadBalancer ]   │<-- Load Balances      │     [ ServerB ]          │
    │ [ ServerA-1 (Node 1) ]   │    to App Tier        │     [ ClientA ]          │
    │ [ ServerA-2 (Node 2) ]   │                       │      (VPN Tester)        │
    └────────────┬─────────────┘                       └──────────────────────────┘
                 │ (172.20.10.1)
    ┌────────────┴─────────────┐
    │    CORE PROTECTED LAN    │
    │      172.20.10.0/24      │
    │                          │
    │ [ PostgreSQL 15 ] (DB)   │ 
    │ [ Redis 7 ] (Cache)      │
    │ [ Syslog / Promtail ]    │ --> Feeds to dashboard
    │ [ Grafana Dashboard ]    │
    └──────────────────────────┘
```

---

## 📁 Project Structure

```text
network-lab/lab7/
├── docker-compose.yml             # Global network topology & service deployment
├── README.md
│
├── automation/                    # Node & Container Engineering
│   ├── ClientA/                   # Test node specifically for firing traffic thru VPN
│   ├── LoadBalancer/              # Nginx gateway distributing to ServerA tier
│   │   └── nginx.conf 
│   ├── Observability/             # Dashboards and Analytics
│   │   ├── grafana/provisioning/  # Pre-built Enterprise Dashboards
│   │   ├── loki-config.yml
│   │   └── promtail-config.yml
│   ├── R1/                        # Master Router: FRR (OSPF/VRRP) & StrongSwan (IPsec)
│   │   ├── Dockerfile
│   │   ├── ipsec.conf & ipsec.secrets
│   │   └── init.sh                # IPTables (DNAT, SNAT) mappings
│   ├── R2/                        # Branch Router handling IPsec return path
│   ├── R3/                        # Backup Router holding VRRP Priority 100
│   ├── ServerA/                   # Clustered HQ App Tier connecting to DB/Cache
│   ├── ServerB/                   # Branch App Tier connecting via VPN
│   └── Syslog/                    # Rsyslog configs aggregating router subsystem logs
│
├── config/                        # Core routing configuration maps (zebra/ospfd/vrrpd)
│   ├── R1/daemons & frr.conf
│   ├── R2/daemons & frr.conf
│   └── R3/daemons & frr.conf
│
├── scripts/                       # Lab Integration Tools
│   └── test_resiliency.py         # Full automated script triggering API and Network checks ⭐
│
└── report/                        # Enterprise Whitepaper Documentation
    └── LAB7_Report.md
```

---

## 🚀 Quick Start Deployment

### Prerequisites
- Docker Desktop or Engine (with `docker-compose` capabilities)
- Python 3.x (to execute `scripts/test_resiliency.py`)

### 1. Build and Subnet Initialization
```bash
# Execute in the lab7 root directory
docker-compose up -d --build
```
> *Wait exactly 10–15 seconds post-boot. The L3 routers (`zebra`, `ospfd`) must calculate network adjacencies and IKEv2 must negotiate encryption keys before traffic freely flows.*

### 2. Verify Initial Container State
```bash
docker compose ps
```

---

## 🧪 Resiliency Test Suite

Forget manual curl tests. We employ a customized Python suite that checks LoadBalancing efficiency and tests the encapsulation of the IPsec Gateway.

### Run Full Pipeline
```bash
python3 scripts/test_resiliency.py
```

### 📋 Expected Resiliency Validation Output
```text
  ╔══════════════════════════════════════════════════╗
  ║   Lab 7 — Network Engineering Validation Suite   ║
  ║   Automated Topology Verification Script         ║
  ╚══════════════════════════════════════════════════╝

  TEST 1: Connectivity & Container Health
  ✅ PASS  Container R1 running
           └─ docker inspect → Running=true
  ✅ PASS  Container ServerA-1 running
           └─ docker inspect → Running=true
  ... (All 10 Containers Evaluated)

  TEST 2: NGINX Load Balancer Distribution
  ℹ  Sending 10 requests to LoadBalancer via ClientA (through VPN)...
  ✅ PASS  Traffic distributed to 2+ nodes
           └─ Nodes seen: {'Srv2': 5, 'Srv1': 5}

  TEST 3: IPsec Site-to-Site VPN Check
  ✅ PASS  IPsec SA Established
           └─ R1 reports active tunnel bounds with R2

  ✅ Lab 7 Verification Suite Completed.
```

---

## 🔐 Security & Network Architecture

| Enterprise Control | Engineering Implementation |
|--------------------|----------------------------|
| **Crypted Tunneling** | StrongSwan (IKEv2) encapsulates `172.20.10.0/24` through `172.30.1.X` utilizing `AES-256-CBC` and `SHA-256`. |
| **High Availability** | `vrrpd` floats Virtual IPs `.1` natively across R1/R3 hardware MAC addresses ensuring zero downtime. |
| **Dynamic Discovery** | `ospfd` actively drops dead branches via Dead Interval metrics preventing traffic balckholes. |
| **Edge Threat Protection** | `iptables` manually processes `-A PREROUTING` to DNAT ingress web traffic securely to Nginx proxy. |
| **Stateful Firewalling** | `iptables -A FORWARD -m state --state INVALID -j DROP` drops malformed packets protecting the LANs. |

---

## 🌐 Endpoints & Dashboards

| Service Endpoint | Target Output |
|------------------|---------------|
| `http://localhost:80/` | Proxies natively into API tier demonstrating round-robin distributions via NGINX. |
| `http://localhost:3000/`| **Grafana Dashboard** (Login: `admin` / `admin`). Pre-provisioned to directly graph OSPF/IPsec event timelines. |

---

## ⚡ Technical Executions (Failover & Cryptography)

### Checking Deep Cryptography (IPsec Status)
Instead of pinging logic, we verify kernel Security Associations matching physical deployments.
```bash
$ docker exec R1 ipsec status

Security Associations (2 up, 0 connecting):
      branch[7]: ESTABLISHED 2 minutes ago, 172.30.1.1...172.30.1.2
      branch{25}:  INSTALLED, TUNNEL, reqid 1, ESP SPIs: c02f69a2_i c045c09f_o
      branch{25}:   172.20.10.0/24 172.20.30.0/24 === 172.20.20.0/24
```

### OSPF & VRRP Transition Tracking
To demonstrate true network redundancy, pull the plug on R1.
```bash
docker stop R1
```
*(Check Grafana or OSPF Route Tables on R3. R3 naturally absorbs the `172.20.10.1` gateway duties without App Tiers noticing).*

---

## 📊 Comprehensive Test Plan (25 Test Matrix)

*For detailed explanations, refer to [LAB7_Report.md](report/LAB7_Report.md).*

| ID | Test Case | Expected Condition | Status | Method / Command |
|---|---|---|---|---|
| C-01 | R1, R2, R3 Health | Containers Running | ✅ PASS | `test_resiliency.py` |
| C-02 | App & DMZ Tier | Nodes running flawlessly | ✅ PASS | `test_resiliency.py` |
| C-03 | Databases (PSQL/Redis) | Ports strictly internal | ✅ PASS | Network inspection |
| R-04 | WAN Routing | ICMP allowed on `isp1_net` | ✅ PASS | Router kernel forwarding |
| O-05 | OSPF Discovery | `172.20.20.0` injected natively | ✅ PASS | `docker exec R1 vtysh` |
| O-06 | OSPF Failover | Dead Routes dropped (<10s) | ✅ PASS | `docker stop R1` & read logs |
| V-07 | VRRP Primary | R1 holds `172.20.10.1` | ✅ PASS | `vtysh -c "show vrrp"` |
| V-08 | VRRP Failover Backup | R3 absorbs `172.20.10.1` instantly | ✅ PASS | `docker stop R1` & vtysh eval |
| S-09 | VPN Payload Encryption | ESP payload obscures source IP | ✅ PASS | IPsec `statusall` |
| S-10 | VPN Connection Alive | SA status: `ESTABLISHED` | ✅ PASS | `test_resiliency.py` |
| S-11 | Web E2E Traversal | ClientA accesses LoadBalancer | ✅ PASS | Python API fetch |
| L-12 | Load Balancer Traffic | Traffic divided fairly (50/50 split)| ✅ PASS | API output inspection |
| D-13 | Redis DB Layer Hit | Microservices pull KeyValues | ✅ PASS | Node JS/Python driver hooks |
| D-14 | PostgreSQL Commit | Log rows correctly incremented | ✅ PASS | Container volume assertion |
| F-15 | IPTables DNAT | Edge gateway forwards Port 80 | ✅ PASS | `iptables -L -t nat -v -n` |
| F-16 | SNAT Outbound Access | Containers reach Ext-Internet | ✅ PASS | `iptables POSTROUTING` mask |
| M-17 | Rsyslog Capture | OSPF logs written to folder | ✅ PASS | UDP port 514 aggregation |
| M-18 | Promtail File Scraping | Logs translated to structured JSON | ✅ PASS | Promtail output verification |
| M-19 | Loki Time-Serie Store | Stored logs retained persistently| ✅ PASS | HTTP Port 3100 Querying |
| M-20 | Grafana Dashboards | Provisioned UI populating graphs | ✅ PASS | Access http://localhost:3000 |

*... (Extensive execution of remaining network validation checks completed via testing script).*

---

## 🛑 Stop & Cleanup

To safely disassemble the enterprise infrastructure:
```bash
# Dismantle routes and containers
docker-compose down

# Destructive Clean (Wipes PostgreSQL persistent data and Observability logs)
docker-compose down -v --remove-orphans
```
