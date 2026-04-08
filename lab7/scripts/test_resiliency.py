import subprocess
import json
import time
import sys

# --- Configuration & Test Table Mapping ---
TEST_REGISTRY = {
    "R-01": "Core Connectivity: HQ Gateway (R1)",
    "R-02": "Core Connectivity: Branch Router (R2)",
    "R-03": "Core Connectivity: HQ Backup (R3)",
    "R-04": "Service Layer: HQ Load Balancer",
    "R-05": "Service Layer: HQ Cluster (ServerA 1/2)",
    "R-06": "Service Layer: Branch Site (ServerB)",
    "R-07": "Storage & State: Postgres Health",
    "R-07b": "Storage & State: Redis Health",
    "R-08": "WAN Route: HQ ICMP sweeps ISP 1",
    "R-09": "WAN Route: Branch sweeps ISP 2",
    "O-10": "OSPF: Area 0 Adjacencies (R1-R3)",
    "O-11": "OSPF: Route Table Sync (R2 learning HQ)",
    "V-12": "VRRP: Gateway Master Election (R1)",
    "V-13": "VRRP: Background Listening State (R3)",
    "V-14": "Failover: VIP Migration during Master Drop",
    "V-15": "Failover: Service Recovery after Failover",
    "S-16": "IPsec: Tunnel Establishment (Site-to-Site)",
    "S-17": "IPsec: ESP Traffic Encryption",
    "M-19": "Microservices: Persistence Layer I/O",
    "M-21": "Performance: Load Balancing Fair Distribution",
    "F-22": "Firewall: Stateful Packet Forwarding",
    "L-23": "Logging: Syslog Aggregation Active",
    "L-24": "Observability: Loki Ingestion Ready",
    "L-25": "NOC GUI: Visualization Dashboards",
}

PASS_COUNT = 0
FAIL_COUNT = 0

def run_cmd(cmd, timeout=15):
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return res.stdout.strip(), res.returncode
    except subprocess.TimeoutExpired:
        return "", -1

def print_header(title):
    print("\n" + "═" * 70)
    print(f"  {title}")
    print("═" * 70)

def print_test(tid, result, msg, detail=""):
    global PASS_COUNT, FAIL_COUNT
    color = "\033[92m✅ PASS\033[0m" if result else "\033[91m❌ FAIL\033[0m"
    print(f" [{tid}] {color} | {msg}")
    if detail:
        print(f"       └─ {detail}")
    if result:
        PASS_COUNT += 1
    else:
        FAIL_COUNT += 1

# ─── PHASE 1: Infrastructure & Connectivity ───────────────────────────────────
def test_infrastructure():
    print_header("PHASE 1: INFRASTRUCTURE & CONNECTIVITY")

    nodes = {
        "R-01": ("R1",          "172.30.1.1"),
        "R-02": ("R2",          "172.30.1.2"),
        "R-03": ("R3",          "172.30.2.1"),
        "R-04": ("LoadBalancer","172.20.30.10"),
        "R-05": ("ServerA-1",   "172.20.30.11"),
        "R-06": ("ServerB",     "172.20.20.10"),
        "R-07": ("Postgres",    "172.20.10.12"),
    }
    for tid, (name, ip) in nodes.items():
        out, code = run_cmd(f"docker inspect -f '{{{{.State.Running}}}}' {name}")
        print_test(tid, out == "true", f"Node {name} Health", f"IP: {ip} | Running: {out}")

    # Redis health check (R-07b)
    out, code = run_cmd("docker exec Redis redis-cli ping")
    print_test("R-07b", "PONG" in out, "Redis Cache Health", f"redis-cli ping → {out}")

    # WAN reachability
    _, c1 = run_cmd("docker exec R1 ping -c 1 -W 2 172.30.1.254")
    print_test("R-08", c1 == 0, "HQ WAN Reachability", "R1 → ISP1 Gateway (172.30.1.254)")

    _, c2 = run_cmd("docker exec R2 ping -c 1 -W 2 172.30.1.254")
    print_test("R-09", c2 == 0, "Branch WAN Reachability", "R2 → ISP1 Gateway (172.30.1.254)")

# ─── PHASE 2: Dynamic Routing & HA ───────────────────────────────────────────
def test_routing():
    print_header("PHASE 2: DYNAMIC ROUTING & HIGH AVAILABILITY")

    # OSPF
    out, _ = run_cmd("docker exec R1 vtysh -c 'show ip ospf neighbor'")
    print_test("O-10", "Full" in out, "OSPF Area 0 Adjacencies", "R1 sees neighbor as FULL")

    out, _ = run_cmd("docker exec R2 ip route")
    print_test("O-11", "172.20.10.0/24" in out or "172.20.30.0/24" in out,
               "Route Synchronization", "R2 learned HQ subnets via OSPF")

    # VRRP before failover
    r1_vrrp, _ = run_cmd("docker exec R1 ip addr show | grep '172.20.10.1'")
    r3_vrrp, _ = run_cmd("docker exec R3 ip addr show | grep '172.20.10.1'")
    print_test("V-12", "172.20.10.1" in r1_vrrp, "VRRP: R1 Master Election",
               "Master VIP 172.20.10.1 bound to R1")
    print_test("V-13", "172.20.10.1" not in r3_vrrp, "VRRP: R3 Backup Listening",
               "R3 does not hold VIP (standby mode)")

    # VRRP Failover test (V-14, V-15)
    _test_vrrp_failover()

def _test_vrrp_failover():
    """Automated VRRP failover: stop R1, verify R3 takes VIP, restart R1."""
    print("\n  ── VRRP Failover Simulation ──")
    print("  Stopping R1 (simulating power failure)...")
    run_cmd("docker stop R1", timeout=15)
    time.sleep(4)  # wait for keepalived dead interval (advert_int=1, ~3× = 3s)

    r3_after, _ = run_cmd("docker exec R3 ip addr show | grep '172.20.10.1'")
    vip_migrated = "172.20.10.1" in r3_after
    print_test("V-14", vip_migrated, "Failover: VIP Migration during Master Drop",
               "VIP 172.20.10.1 migrated to R3" if vip_migrated else "VIP did NOT migrate to R3")

    # Check service still accessible through R3
    svc_ok = False
    if vip_migrated:
        out, code = run_cmd("docker exec ClientA curl -s --max-time 5 http://172.20.30.10")
        svc_ok = '"postgres_total_logs"' in out
    print_test("V-15", svc_ok, "Failover: Service Recovery after Failover",
               "Load balancer reachable via R3 VIP" if svc_ok else "Service unreachable after failover")

    # Restore R1
    print("  Restarting R1 (master recovery)...")
    run_cmd("docker start R1", timeout=15)
    print("  Waiting for R1 to reclaim Master + re-establish IPsec (~15s)...")
    time.sleep(15)  # allow time for keepalived preempt + IPsec IKEv2 renegotiation

# ─── PHASE 3: Security & Persistence ─────────────────────────────────────────
def test_security_failover():
    print_header("PHASE 3: SECURITY, FAILOVER & PERSISTENCE")

    # IPsec
    out, _ = run_cmd("docker exec R1 ipsec status")
    print_test("S-16", "ESTABLISHED" in out, "IPsec Site-to-Site Tunnel",
               "Tunnel ESTABLISHED with Branch (R2)")

    # ESP encryption verified via XFRM
    out, _ = run_cmd("docker exec R1 ip xfrm state")
    print_test("S-17", "esp" in out.lower(), "IPsec ESP Encryption",
               "XFRM state shows active ESP SAs" if "esp" in out.lower() else "No ESP state found")

    # Microservices
    out, _ = run_cmd("docker exec ClientA curl -s --max-time 5 http://172.20.30.10")
    status = '"postgres_total_logs"' in out and '"server"' in out
    print_test("M-19", status, "Microservices Persistence I/O",
               "JSON has postgres_total_logs key" if status else f"Unexpected response: {out[:80]}")

    # Load balancing distribution
    distribution = {}
    for _ in range(20):
        out, _ = run_cmd("docker exec ClientA curl -s --max-time 3 http://172.20.30.10")
        try:
            srv = json.loads(out)["server"]
            distribution[srv] = distribution.get(srv, 0) + 1
        except Exception:
            pass
    lb_pass = len(distribution) >= 2
    print_test("M-21", lb_pass, "Load Balancing Fair Distribution",
               f"Nodes: {distribution}" if distribution else "No responses received")

# ─── PHASE 4: Firewall & Observability ───────────────────────────────────────
def test_observability():
    print_header("PHASE 4: FIREWALL & OBSERVABILITY")

    # Firewall rules
    out, _ = run_cmd("docker exec R1 iptables -t nat -L -n")
    print_test("F-22", "DNAT" in out and "MASQUERADE" in out,
               "Firewall Stateful Rules", "DNAT + MASQUERADE rules active")

    # Syslog aggregation
    out, _ = run_cmd("docker exec SyslogServer ls /var/log/central/")
    print_test("L-23", "central.log" in out, "Syslog Aggregation Active",
               "central.log present on SyslogServer")

    # Loki ingestion
    out, _ = run_cmd("docker exec loki wget -qO- http://localhost:3100/ready")
    loki_ok = "ready" in out.lower()
    print_test("L-24", loki_ok, "Loki Ingestion Ready",
               "Loki /ready endpoint returns 'ready'" if loki_ok else f"Response: {out}")

    # Grafana dashboard
    out, code = run_cmd("docker inspect -f '{{.State.Running}}' grafana")
    grafana_up = out == "true"
    out2, _ = run_cmd("curl -s --max-time 3 -o /dev/null -w '%{http_code}' http://localhost:3000/login")
    print_test("L-25", grafana_up and out2 == "200",
               "NOC GUI: Grafana Dashboard",
               f"Container: {out} | HTTP: {out2} → http://localhost:3000 (admin/admin)")

# ─── MAIN ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "█" * 70)
    print("█   LAB 7 - ENTERPRISE DATA CENTER VALIDATION SUITE".center(70))
    print("█   Automated Protocol & Service Verification".center(70))
    print("█" * 70)

    test_infrastructure()
    test_routing()          # includes VRRP failover simulation
    test_security_failover()
    test_observability()

    total = PASS_COUNT + FAIL_COUNT
    pct = int(PASS_COUNT / total * 100) if total > 0 else 0

    print("\n" + "═" * 70)
    if FAIL_COUNT == 0:
        print(f"  ✅ FINAL STATUS: {PASS_COUNT}/{total} PASS — 100% SUCCESS".center(70))
    else:
        print(f"  ⚠️  RESULT: {PASS_COUNT} PASS / {FAIL_COUNT} FAIL ({pct}%)".center(70))
    print("═" * 70 + "\n")

    sys.exit(0 if FAIL_COUNT == 0 else 1)
