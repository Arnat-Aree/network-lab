# Lab 6 Network Infrastructure Setup 
*(การตั้งค่าโครงสร้างพื้นฐานเครือข่ายสำหรับ Lab 6)*

โปรเจกต์นี้เป็นการจำลองโครงสร้างพื้นฐานเครือข่ายระดับองค์กรแบบครบวงจรโดยใช้ Docker และ FRRouting (FRR) ซึ่งจะสาธิตการทำงานของระบบหาเส้นทางแบบไดนามิก (OSPF), การทำ NAT, การตรวจสอบสถานะการเชื่อมต่อ (IP SLA) และการแบ่งสัดส่วนและจัดเตรียมเครือข่าย

---

## 🏗 Network Architecture

แลปนี้ประกอบไปด้วยวงเน็ตเวิร์ค 4 วง และ Docker Container จำนวน 6 ตัวดังนี้

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

### Networks
- **`internet_net`** (`172.30.0.0/24`): จำลองเครือข่ายอินเทอร์เน็ตภายนอก
- **`isp_net`** (`172.31.0.0/29`): เครือข่ายเชื่อมต่อภายในแบบจุดต่อจุดระหว่าง R1 และ R2
- **`lan_a_net`** (`172.20.10.0/24`): เครือข่ายแลนภายใน A
- **`lan_b_net`** (`172.20.20.0/24`): เครือข่ายแลนภายใน B

### Nodes / Containers
1. **R1 (Gateway Router)**
   - ทำหน้าที่เป็น Gateway หลักสำหรับออกอินเทอร์เน็ต
   - ทำ NAT เพื่อให้เครื่องในวง LAN ออกเน็ตได้
   - ประมวลผลและแลกเปลี่ยนเส้นทางด้วยโปรโตคอล OSPF ร่วมกับ R2
2. **R2 (Internal Branch Router)**
   - เราเตอร์สาขา ทำหน้าที่เชื่อม LAN B ให้คุยกับวงอื่นและออกเน็ตผ่าน R1 ได้
   - รัน OSPF เพื่ออัปเดตเส้นทาง
3. **ServerA**
   - เซิร์ฟเวอร์ในวง LAN A
4. **ServerB**
   - เซิร์ฟเวอร์ในวง LAN B
5. **ClientA**
   - เครื่องลูกข่ายสำหรับทดสอบในวง LAN A
6. **InternetTester**
   - เครื่องตัวแทนเซิร์ฟเวอร์ปลายทางบนโลกอินเทอร์เน็ต เพื่อใช้ทดสอบการออกเน็ต

---

## ✨ Features Implemented

- **Dynamic Routing (OSPF):** R1 และ R2 แลกเปลี่ยนเส้นทางกันได้อัตโนมัติผ่าน FRRouting (`frr.conf`) ไม่ต้องคอยเซ็ต Static Route เอง
- **NAT / Firewall:** ตั้งค่าการแปลงไอพีและการกรองเส้นทางสำหรับทราฟฟิกในวง LAN ผ่าน `iptables` ไว้ที่ R1
- **IP SLA / Failover Monitoring:** มีสคริปต์เช็คความพร้อมการเชื่อมต่อ หากเส้นทางไหนมีปัญหาจะปรับพฤติกรรมเราติ้งให้เองแบบอัตโนมัติ (`ip_sla.sh`)
- **Automated Container Provisioning:** ใช้ `Dockerfile` และสคริปต์คอนฟิกเริ่มต้นเพื่อกำหนด Default Route และรันการตั้งค่าประจำคอนเทนเนอร์ให้อัตโนมัติเมื่อสั่งรัน

---

## 🚀 How to Run

1. เช็คให้แน่ใจว่าติดตั้ง Docker และ Docker Compose ในเครื่องเรียบร้อยแล้ว
2. โคลนและเข้าไปยังโฟลเดอร์โปรเจกต์:
   ```bash
   git clone https://github.com/Arnat-Aree/network-lab.git
   cd network-lab
   ```
3. เริ่มสร้างตัวคอนเทนเนอร์และเซตอัพโครงสร้างระบบ:
   ```bash
   docker-compose up -d --build
   ```
4. เช็คความพร้อมว่าคอนเทนเนอร์ทำงานครบทั้ง 6 ตัว:
   ```bash
   docker ps
   ```

---

## 🧪 Testing the Infrastructure

หลังจากรันระบบเสร็จ สามารถใช้คำสั่งเหล่านี้เพื่อทดสอบการสื่อสารของเครือข่าย

**1. Test OSPF Routing (LAN A to LAN B):**
ตรวจสอบการสื่อสารข้าม LAN ถ้าระบบ OSPF ทำงาน Client A (172.20.10.50) จะต้องปิงเจอ Server B (172.20.20.10) ได้
```bash
docker exec -it ClientA ping 172.20.20.10
```

**2. Test NAT and Internet Access:**
ทดสอบปิงจากวง LAN ออกไปสู่โลกอินเทอร์เน็ตภายนอก (ผ่าน R1)
```bash
docker exec -it ClientA ping 172.30.0.100
```

**3. Check FRR Routing Tables on R1:**
ส่องดูตารางค้นหาเส้นทางแบบอัตโนมัติบน R1 (มองหารูทที่นำหน้าด้วย `O` ซึ่งย่อมาจาก OSPF)
```bash
docker exec -it R1 vtysh -c "show ip route"
```

---

## 📁 Project Structure

```text
.
├── automation/                 # แหล่งจัดเก็บสคริปต์และคอนฟิกเริ่มต้นของอุปกรณ์
│   ├── ClientA/                # สคริปต์และการตั้งค่าสำหรับเครื่อง ClientA
│   ├── R1/                     # สคริปต์เริ่มต้นระบบ ปรับแต่งเส้นทาง Router 1
│   ├── R2/                     # สคริปต์เริ่มต้นระบบ ปรับแต่งเส้นทาง Router 2
│   ├── ServerA/                # สคริปต์สำหรับเริ่มต้น Service เครื่อง ServerA
│   └── ServerB/                # สคริปต์สำหรับเริ่มต้น Service เครื่อง ServerB
├── config/                     # โฟลเดอร์เก็บค่าคอนฟิกของเราเตอร์
│   ├── R1/                     # คอนฟิกการทำงาน FRRouting และ OSPF ของ Router 1
│   └── R2/                     # คอนฟิกการทำงาน FRRouting และ OSPF ของ Router 2
├── docker-compose.yml          # ไฟล์หลักที่ใช้ระบุโครงสร้างการเชื่อมต่อเครือข่ายทั้งหมด
└── README.md                   # เอกสารอธิบายโปรเจกต์
```
