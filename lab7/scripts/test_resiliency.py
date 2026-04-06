import subprocess
import json
import time

def run_cmd(cmd):
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return res.stdout.strip(), res.returncode
    except subprocess.TimeoutExpired:
        return "", -1

def print_header(title):
    print("\n" + "═" * 60)
    print(f"  {title}")
    print("═" * 60)

def print_pass(msg, detail):
    print(f"  \033[92m✅ PASS\033[0m  {msg}")
    print(f"           └─ {detail}")

def print_fail(msg, detail):
    print(f"  \033[91m❌ FAIL\033[0m  {msg}")
    print(f"           └─ {detail}")

def test_containers():
    print_header("TEST 1: Connectivity & Container Health")
    containers = ["R1", "R2", "R3", "ServerA-1", "ServerA-2", "ServerB", "Postgres", "Redis", "LoadBalancer", "ISPRouter"]
    for c in containers:
        out, code = run_cmd(f"docker inspect -f '{{{{.State.Running}}}}' {c}")
        if out == "true":
            print_pass(f"Container {c} running", "docker inspect → Running=true")
        else:
            print_fail(f"Container {c} NOT running", f"State: {out}")

def test_load_balancer():
    print_header("TEST 2: NGINX Load Balancer Distribution")
    print("  ℹ  Sending 10 requests to LoadBalancer via ClientA (through VPN)...")
    distribution = {}
    
    for i in range(10):
        out, code = run_cmd("docker exec ClientA curl -s -m 5 http://172.20.30.10")
        if code == 0 and out:
            try:
                data = json.loads(out)
                node = data.get("server", "Unknown")
                distribution[node] = distribution.get(node, 0) + 1
            except:
                pass
    
    if len(distribution) >= 2:
        print_pass("Traffic distributed to 2+ nodes", f"Nodes seen: {distribution}")
    elif len(distribution) == 1:
        print_fail("Traffic NOT distributed", f"Only 1 node handled traffic: {distribution}")
    else:
        print_fail("LoadBalancer Unreachable", "Failed to get responses from LoadBalancer")

def test_ipsec_tunnel():
    print_header("TEST 3: IPsec Site-to-Site VPN Check")
    out, code = run_cmd("docker exec R1 ipsec status")
    if "ESTABLISHED" in out:
        print_pass("IPsec SA Established", "R1 reports active tunnel bounds with R2")
    else:
        print_fail("IPsec SA Down", "No ESTABLISHED connections found")

if __name__ == "__main__":
    print("\n  ╔══════════════════════════════════════════════════╗")
    print("  ║   Lab 7 — Network Engineering Validation Suite   ║")
    print("  ║   Automated Topology Verification Script         ║")
    print("  ╚══════════════════════════════════════════════════╝\n")
    test_containers()
    test_load_balancer()
    test_ipsec_tunnel()
    print("\n  \033[92m✅ Lab 7 Verification Suite Completed.\033[0m\n")
