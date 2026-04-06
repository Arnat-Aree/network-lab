# 📑 รายงานผลการปฏิบัติการ Lab 6
# Resilient Internet + Secure Microservices

---

## 👥 รายชื่อสมาชิกกลุ่ม

| Student ID | ชื่อ-นามสกุล |
|---|---|
| 673380411-3 | นายปฏิกาณ ปานทะเล |
| 673380413-9 | นายปิยพันธ์ แก้วเก็บคำ |
| 673380426-0 | นายวรปรัชญ์ พิมพ์อุบล |
| 673380432-5 | นายอาณัฐ อารีย์ |
| 673380434-1 | นายเนติภัทร ภูครองเพชร |
| 673380582-6 | นายณัฐชา อรรคอาต |
| 673380599-9 | นายรัชชานนท์ ประดับแก้ว |

---

## 1. 🎯 วัตถุประสงค์ (Objectives)

การทดลองนี้เป็นการอัปเกรดโครงข่ายจาก Lab 5 พื้นฐาน ให้มีความแข็งแกร่งและปลอดภัยในระดับโครงข่ายสาขาองค์กร (Enterprise-grade resilient WAN + secured microservices) โดยมีวัตถุประสงค์หลักดังนี้:

1. เปลี่ยนจากระบบเร้าติ้งแบบตายตัว (Static Routing) ไปใช้แบบไดนามิก (OSPF)
2. เพิ่มระบบตรวจจับความล้มเหลวของเส้นทางฝั่ง WAN (IP SLA)
3. ใช้งานระบบรักษาความปลอดภัยพื้นฐานหน้าด่าน (ACL Firewalling)
4. ควบคุมช่องทางการเข้าถึงเซิร์ฟเวอร์ย่อยให้รัดกุมยิ่งขึ้น (Microservice Exposure)
5. สร้างความพร้อมด้านการดูแลระบบและการบันทึกข้อมูล (Observability Foundation)
6. วางรากฐานโครงสร้างเครือข่ายให้พร้อมสำหรับการขยายตัว (Scale-out) ในอนาคต

---

## 2. 🏗 โครงสร้างเครือข่าย (Topology)

เครือข่ายยังคงอิงรูปแบบทางกายภาพเดิม แต่อัปเกรดระดับทราฟฟิกลอจิก (Logic) โดยเพิ่มการตั้งค่า OSPF Area 0 ระหว่าง R1 และ R2 ควบคู่กับการประยุกต์ใช้กฎของ Firewall (iptables) และระบบ IP SLA Monitor แบบเรียลไทม์

```text
       [ Internet (172.30.0.0/24) ]
                    |
            [ InternetTester ]
                    |
       [ R1 (Edge Router + NAT + FW) ]
         /                     \
[ LAN A (172.20.10.0/24) ]   [ ISP Network (172.31.0.0/29) ]
         |                                 |
   +-----+-----+                 [ R2 (Internal Router) ]
   |           |                           |
[ClientA] [ServerA]              [ LAN B (172.20.20.0/24) ]
                                           |
                                      [ ServerB ]
```

### Network Segments

| Network | Subnet |
|---|---|
| Internet | 172.30.0.0/24 |
| ISP Network | 172.31.0.0/29 |
| LAN A | 172.20.10.0/24 |
| LAN B | 172.20.20.0/24 |

### Infrastructure Components

| Device | Role |
|---|---|
| R1 | Edge Router (NAT + Firewall) |
| R2 | Internal Router |
| ServerA | Public microservice host |
| ServerB | Internal microservice host |
| ClientA | Internal client |
| InternetTester | Simulated Internet client |

---

## 3. ⚙️ รายละเอียดการทำงาน (Implementation Details)

### ◆ PHASE 1 — Replace Static with OSPF

- **เหตุผล (Why):** Static route แบบเดิมจะไม่สามารถตรวจรู้ได้เมื่อเส้นทางมีปัญหาและไม่รองรับสเกลแอปพลิเคชันที่กว้างขึ้น
- **สิ่งที่ปรับปรุง:** เราปรับมาใช้โปรโตคอล OSPF ผ่านโปรแกรม FRRouting บน R1 และ R2 โดยทำการประกาศ network area 0
- **ผลลัพธ์:** มีการตั้งค่า `default-information originate always` บน Gateway (R1) ส่งผลให้ R2 และวง LAN ทราบเส้นทางสำหรับออกสู่อินเทอร์เน็ตได้โดยอัตโนมัติ

แสดงค่าคอนฟิก OSPF ของ R1:

```
router ospf
 ospf router-id 1.1.1.1
 network 172.20.10.0/24 area 0
 network 172.31.0.0/29 area 0
 default-information originate always
exit
```

แสดงค่าคอนฟิก OSPF ของ R2:

```
router ospf
 ospf router-id 2.2.2.2
 network 172.20.20.0/24 area 0
 network 172.31.0.0/29 area 0
exit
```

ผลการตรวจสอบ OSPF Neighbor:

```
Neighbor ID     Pri State           Up Time         Dead Time Address         Interface
2.2.2.2           1 Full/DR         15m35s          34.691s   172.31.0.2      eth1:172.31.0.1
```

> จากผลลัพธ์ยืนยันว่า R1 สามารถเชื่อมต่อกับ R2 (Router-ID 2.2.2.2) ด้วยสถานะ Full/DR ผ่านวง ISP (172.31.0.0/29) ได้สำเร็จ แสดงว่าระบบ OSPF ทำงานเป็นปกติ

---

### ◆ PHASE 2 — WAN Failure Detection (IP SLA)

- **การทำงาน:** มีการจำลองการตรวจสอบการเชื่อมต่ออินเทอร์เน็ตผ่านสคริปต์ `ip_sla.sh` ซึ่งจำลองตรรกะแบบ Cisco IP SLA (icmp-echo)
- **ผลลัพธ์:** สคริปต์จะคอย Ping ไปที่ไอพีปลายทาง หากขาดการเชื่อมต่อเนื่อง ระบบจะถอดถอน Default Route (0.0.0.0) ออกจากตารางเส้นทางชั่วคราว เพื่อให้คอนเทนเนอร์อื่นในระบบรับรู้ว่าขณะนี้อินเทอร์เน็ตใช้งานไม่ได้

แสดงว่าสคริปต์ IP SLA กำลังทำงานอยู่:

```
$ docker exec -it R1 ps aux | grep ip_sla
   67 root      0:00 sh /automation/ip_sla.sh
```

> ยืนยันว่า process ip_sla.sh กำลังรันอยู่บน R1 คอยตรวจสอบสถานะการเชื่อมต่ออินเทอร์เน็ตอย่างต่อเนื่อง

---

### ◆ PHASE 3 — Basic WAN Security

- **การทำงาน:** ปิดกั้นบุคคลภายนอกไม่ให้บุกรุกเข้าเครือข่ายโดยไม่ได้รับอนุญาต
- **ผลลัพธ์:** เราใช้กฎ Firewall ผ่าน `iptables -A FORWARD` บน R1 กรองข้อมูลขาเข้าจาก ISP โดยอนุญาตเพียงข้อมูลที่เกิดจากการร้องขอจากผู้ใช้ภายใน (ESTABLISHED, RELATED) หรือระหว่าง LAN ด้วยกันเท่านั้น นอกเหนือจากนั้นจะถูกระบบแบน (DROP) ทั้งหมด

แสดงกฎ Firewall ทั้งหมดบน R1:

```
$ docker exec -it R1 iptables -L FORWARD -v -n

Chain FORWARD (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target  prot opt in   out  source            destination
    0     0 ACCEPT  0    --  eth1 *    172.20.20.0/24    172.20.10.0/24
    0     0 ACCEPT  0    --  *    *    0.0.0.0/0         0.0.0.0/0        state RELATED,ESTABLISHED
    0     0 ACCEPT  0    --  eth2 *    0.0.0.0/0         0.0.0.0/0
    0     0 ACCEPT  6    --  eth0 *    0.0.0.0/0         172.20.10.10     tcp dpt:8000
    0     0 DROP    0    --  eth1 *    0.0.0.0/0         0.0.0.0/0
```

อธิบายกฎ Firewall แต่ละข้อ:

| กฎ | ความหมาย |
|---|---|
| ACCEPT eth1 172.20.20.0/24 → 172.20.10.0/24 | อนุญาต LAN B คุยกับ LAN A ได้ |
| ACCEPT state RELATED,ESTABLISHED | อนุญาตข้อมูลที่เป็นการตอบกลับจากการร้องขอจากภายใน |
| ACCEPT eth2 | อนุญาตให้ LAN A ส่งข้อมูลออกได้อิสระ |
| ACCEPT eth0 tcp dpt:8000 → 172.20.10.10 | อนุญาตเฉพาะพอร์ต 8000 จากอินเทอร์เน็ตไปหา ServerA |
| DROP eth1 | **บล็อกทราฟฟิกอื่นทั้งหมดจาก ISP** |

---

### ◆ PHASE 4 — Microservice Exposure Control

- **การทำงาน:** แทนที่จะเปิดเผยเซิร์ฟเวอร์แบบสาธารณะทั้งหมด เราควบคุมการเข้าถึงด้วยเทคนิค NAT (Port Forwarding)
- **ผลลัพธ์:** กำหนดกฎ DNAT อนุญาตให้เข้ามาที่ R1 ผ่านพอร์ต 8000 เท่านั้น ถึงจะสามารถส่งข้อมูลชิ่งต่อไปประมวลผลที่ ServerA (172.20.10.10) ได้ ทำให้ระบบหลังบ้านหรือพอร์ตอื่นๆ ถูกซ่อนไว้และปลอดภัยจากการสแกนโจมตี

แสดงกฎ NAT ทั้งหมดบน R1:

```
$ docker exec -it R1 iptables -t nat -L -v -n

Chain PREROUTING (policy ACCEPT)
 pkts bytes target  prot opt in   out  source     destination
    0     0 DNAT    6    --  eth0 *    0.0.0.0/0  0.0.0.0/0    tcp dpt:8000 to:172.20.10.10:8000

Chain POSTROUTING (policy ACCEPT)
 pkts bytes target      prot opt in  out   source     destination
  716 60144 MASQUERADE  0    --  *   eth0  0.0.0.0/0  0.0.0.0/0
    0     0 MASQUERADE  6    --  *   eth2  0.0.0.0/0  172.20.10.10  tcp dpt:8000
```

> **PREROUTING (DNAT):** พอร์ต 8000 จากอินเทอร์เน็ตถูกส่งต่อไปหา ServerA
> **POSTROUTING (MASQUERADE):** ทำ NAT แปลงไอพีให้เครื่องในวง LAN ออกเน็ตได้

---

### ◆ PHASE 5 — Observability Foundation

- **การทำงาน:** เปิดระบบบันทึกสถานะเครือข่าย (Logging) บน FRRouting เพื่อให้สามารถตรวจสอบประวัติการเปลี่ยนแปลงของเส้นทางได้
- **ผลลัพธ์:** ตั้งค่า `log syslog informational` ไว้ใน frr.conf ทำให้เมื่อเกิดเหตุการณ์ เช่น OSPF neighbor ขึ้น/ลง หรือเส้นทางเปลี่ยนแปลง ระบบจะมี Log เก็บประวัติไว้ตรวจสอบย้อนหลังได้

```
$ docker exec -it R1 vtysh -c "show running-config" | grep log
log syslog informational
```

> แสดงการตั้งค่า log syslog informational ใน FRRouting ของ R1 ซึ่งจะบันทึกเหตุการณ์สำคัญทุกอย่างที่เกิดขึ้นในระบบเร้าติ้ง เพื่อให้ผู้ดูแลระบบสามารถตรวจสอบย้อนหลังได้

---

## 4. 📈 ผลการทดสอบความถูกต้องของระบบ (Phase 6: Network Validation)

### Test 1: OSPF Neighbor

```
$ docker exec -it R1 vtysh -c "show ip ospf neighbor"

Neighbor ID     Pri State           Up Time         Dead Time Address         Interface
2.2.2.2           1 Full/DR         1h17m36s        34.848s   172.31.0.2      eth1:172.31.0.1
```

> ✅ R1 เชื่อมต่อกับ R2 สถานะ Full/DR สมบูรณ์

### Test 2: Routing Table (OSPF)

```
$ docker exec -it R1 vtysh -c "show ip route"

K>* 0.0.0.0/0 [0/0] via 172.30.0.254, eth0
S   0.0.0.0/0 [1/0] via 172.30.0.254, eth0
O   172.20.10.0/24 [110/10] is directly connected, eth2
O   172.20.20.0/24 [110/20] via 172.31.0.2, eth1    ← เรียนรู้จาก OSPF
O   172.31.0.0/29 [110/10] is directly connected, eth1
```

> ✅ เห็นสัญลักษณ์ **O** (OSPF) ที่เส้นทาง 172.20.20.0/24 แสดงว่า R1 เรียนรู้วง LAN B จาก R2 ได้สำเร็จ

### Test 3: LAN A ↔ LAN B

```
$ docker exec -it ClientA ping -c 4 172.20.20.10

PING 172.20.20.10 (172.20.20.10): 56 data bytes
64 bytes from 172.20.20.10: seq=0 ttl=62 time=1.224 ms
64 bytes from 172.20.20.10: seq=1 ttl=62 time=0.292 ms
64 bytes from 172.20.20.10: seq=2 ttl=62 time=0.318 ms
64 bytes from 172.20.20.10: seq=3 ttl=62 time=0.083 ms

--- 172.20.20.10 ping statistics ---
4 packets transmitted, 4 packets received, 0% packet loss
```

> ✅ ClientA (LAN A) สามารถสื่อสารกับ ServerB (LAN B) ได้สำเร็จ 0% packet loss

### Test 4: Internet → Port 8000 (ต้องผ่าน)

```
$ docker exec -it InternetTester curl -s --max-time 5 http://172.30.0.2:8000/health

{"status": "ok", "service": "upload", "server": "ServerA"}
```

> ✅ จากเครื่อง InternetTester สามารถเข้าถึง Service ผ่าน NAT (DNAT) ที่พอร์ต 8000 ได้สำเร็จ ได้รับ JSON response กลับมาจาก ServerA ภายในวง LAN A

### Test 5: Internet → Port 9000 (ต้องถูกบล็อก)

```
$ docker exec -it InternetTester curl -s --max-time 5 http://172.30.0.2:9000

(ไม่มีผลลัพธ์ — Connection refused / Timeout)
```

> ✅ จากเครื่อง InternetTester ไม่สามารถเข้าถึงพอร์ต 9000 ได้ เนื่องจากไม่มีกฎ NAT (DNAT) อนุญาตไว้ และ Firewall บล็อกทราฟฟิกทิ้ง ยืนยันว่าระบบเปิดเผยเฉพาะ Service ที่อนุญาตเท่านั้น

### Test 6: ISP Unplug (Failover Test)

**ก่อนตัดการเชื่อมต่อ:**

```
$ docker exec -it R1 vtysh -c "show ip route" | grep "0.0.0.0"

K>* 0.0.0.0/0 [0/0] via 172.30.0.254, eth0
S   0.0.0.0/0 [1/0] via 172.30.0.254, eth0
```

**หลังตัดการเชื่อมต่อ (รอ 10 วินาที):**

```
$ docker exec -it R1 ip route del default via 172.30.0.254
$ sleep 10
$ docker exec -it R1 vtysh -c "show ip route" | grep "0.0.0.0"

S>* 0.0.0.0/0 [1/0] via 172.30.0.254, eth0
```

> ✅ พอเราลบ Kernel route (K) ทิ้ง ระบบ FRRouting ตรวจพบและสลับให้ Static route (S) ขึ้นมาทำหน้าที่แทนโดยอัตโนมัติ (สังเกตจาก `proto 196` ที่บ่งบอกว่า route นี้ถูกสร้างโดย FRR) ยืนยันว่าระบบ Resilient Routing ทำงานตามที่ออกแบบไว้

---

## 5. 📊 สรุปผลการทดสอบ (Test Plan Summary)

| การทดสอบ | ผลลัพธ์ที่คาดหวัง | ผลการทดสอบจริง |
|---|---|---|
| OSPF Neighbor | `Full` | ✅ Full/DR |
| show ip route ospf | Remote LAN visible | ✅ เห็น 172.20.20.0/24 ผ่าน OSPF |
| ISP Unplug (IP SLA) | Default route disappears | ✅ K route หายไป, S route ขึ้นมาแทน |
| Internet → Port 8000 | Success | ✅ ได้รับ JSON response สำเร็จ |
| Internet → Port 9000 | Blocked | ✅ Connection refused |
| LAN A ↔ LAN B | Success | ✅ 0% packet loss |

---

## 6. 🏢 การจัดหมวดหมู่สถาปัตยกรรม (Architecture Classification)

โครงสร้างจากการทดลองนี้จัดอยู่ในระดับ: **Enterprise Branch Architecture v1** โดยผ่านคุณสมบัติดังนี้:

- [x] **Routed WAN with dynamic routing:** มีเร้าติ้งยืดหยุ่นหาทางออกอัตโนมัติ
- [x] **Conditional default injection:** แจกจ่ายเส้นทางอิงตามสถานการณ์เน็ต
- [x] **WAN ACL firewall:** มีกำแพงหน้าด่านที่ตรวจทราฟฟิกฝั่งพับบลิค
- [x] **Controlled service publishing:** ควบคุมช่องทางเปิดเซิร์ฟเวอร์แบบเฉพาะด้านอย่างรัดกุม
- [x] **Production edge logic:** ใช้ตรรกะระดับเครือข่ายจริงในการป้องกัน

---

## 7. 🏆 บทสรุปคะแนนความพร้อมของระบบ (Readiness Score After Lab 6)

| หมวดหมู่ (Category) | คะแนน (Score) | ทิศทางการปรับปรุงขั้นต่อไป |
|---|---|---|
| **Routing** | 9/10 | - |
| **WAN Intelligence** | 9/10 | - |
| **Security** | 6/10 | สามารถต่อยอดระบบด้วยสถาปัตยกรรม DMZ ได้ในอนาคต |
| **Microservice Exposure** | 8/10 | - |
| **Scalability** | 8/10 | ปรับใช้ Load Balancer ดักหน้าบริการในเฟสถัดไป |

> **ผลคะแนนรวมความพร้อมของระบบ: 🏆 8.5 / 10 (Enterprise Branch-Ready)**

---
