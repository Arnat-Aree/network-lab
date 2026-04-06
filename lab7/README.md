# Lab 7 — Dual ISP, VPN, DMZ & Load Balancing
*(สถาปัตยกรรมเครือข่ายระดับ Enterprise Data Center)*

อัปเกรดจาก Lab 6 (Enterprise Branch Architecture) ให้มีความทนทาน ปลอดภัย และรองรับโหลดสูงขึ้น

---

## 🎯 Objectives

1. จำลอง Dual ISP เพื่อให้มีทางออกอินเทอร์เน็ต 2 เส้น (Redundancy)
2. เพิ่ม R3 และใช้ HSRP เพื่อให้ Gateway สำรองกันได้ (High Availability)
3. เข้ารหัสการสื่อสารระหว่าง LAN ด้วย Site-to-site VPN
4. สร้างโซน DMZ แยก Server ที่เปิดรับสาธารณะออกจากวงภายใน
5. เพิ่ม Load Balancer ดักหน้า Microservices
6. เพิ่มฐานข้อมูล Redis + PostgreSQL ให้ Microservices
7. รวม Log จากทุก Container ไว้ที่ศูนย์กลาง (Central Logging)

---

## 🏗 Network Architecture

```text
     [ ISP 1 ]          [ ISP 2 ]
         |                   |
        R1 (HSRP Active)   R3 (HSRP Standby)
         \                 /
          \               /
       [ ISP Network (172.31.0.0/29) ]
                  |
          [ R2 (Internal Router) ]
           /              \
   [ DMZ Zone ]       [ LAN B ]
       |                  |
  [Load Balancer]     [ ServerB ]
    /        \            
[ServerA-1] [ServerA-2]
                          
   [ LAN A ]
      |
   [ClientA]
```
*(โครงสร้างนี้เป็นแบบร่าง จะปรับเปลี่ยนตามการออกแบบจริง)*

---

## ✨ Features to Implement

- [ ] Dual ISP with failover
- [ ] HSRP (R1 + R3)
- [ ] Site-to-site VPN
- [ ] DMZ zone
- [ ] Load Balancer (Nginx/HAProxy)
- [ ] Redis + PostgreSQL
- [ ] Central Logging Stack

---

## 🚀 How to Run

```bash
cd lab7
docker-compose up -d --build
```

---

## 📁 Project Structure

```text
lab7/
├── automation/
│   ├── R1/                     # Edge Router 1 (HSRP Active)
│   ├── R2/                     # Internal Router
│   ├── R3/                     # Edge Router 2 (HSRP Standby)
│   ├── ServerA/                # Microservice Server
│   ├── ServerB/                # Internal Server
│   └── ClientA/                # Test Client
├── config/
│   ├── R1/                     # FRR config for R1
│   ├── R2/                     # FRR config for R2
│   └── R3/                     # FRR config for R3
├── docker-compose.yml          # โครงสร้างเครือข่าย Lab 7
├── report/                     # รีพอร์ตผลการทดลอง
└── README.md                   # เอกสารนี้
```
