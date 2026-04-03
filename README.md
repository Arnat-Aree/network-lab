# Lab 6 Network Infrastructure Setup 
*(การตั้งค่าโครงสร้างพื้นฐานเครือข่ายสำหรับ Lab 6)*

This project simulates a complete, multi-container enterprise network infrastructure using Docker and FRRouting (FRR). It demonstrates dynamic routing (OSPF), Network Address Translation (NAT), High Availability / Link monitoring (IP SLA), and containerized network segmentation.
*(โปรเจกต์นี้เป็นการจำลองโครงสร้างพื้นฐานเครือข่ายระดับองค์กรแบบครบวงจรโดยใช้ Docker และ FRRouting (FRR) ซึ่งจะสาธิตการทำงานของระบบหาเส้นทางแบบไดนามิก (OSPF), การทำ NAT, การตรวจสอบสถานะการเชื่อมต่อ (IP SLA) และการแบ่งสัดส่วนและจัดเตรียมเครือข่าย)*

---

## 🏗 Network Topology (โครงสร้างเครือข่าย)

The lab consists of 4 distinct IP networks and 6 Docker containers:
*(แลปนี้ประกอบไปด้วยวงเน็ตเวิร์ค 4 วง และ Docker Container จำนวน 6 ตัวดังนี้)*

### Networks (วงเครือข่าย)
- **`internet_net`** (`172.30.0.0/24`): Simulates the external Internet network. *(จำลองเครือข่ายอินเทอร์เน็ตภายนอก)*
- **`isp_net`** (`172.31.0.0/29`): The point-to-point network connecting Router 1 to Router 2. *(เครือข่ายที่เชื่อมต่อกันระหว่าง R1 และ R2)*
- **`lan_a_net`** (`172.20.10.0/24`): Internal LAN A. *(เครือข่ายแลนภายใน A)*
- **`lan_b_net`** (`172.20.20.0/24`): Internal LAN B. *(เครือข่ายแลนภายใน B)*

### Nodes / Containers (คุณสมบัติของแต่ละ Container)
1. **R1 (Gateway Router)**
   - Acts as the main gateway to the Internet. *(ทำหน้าที่เป็น Gateway หลักสำหรับออกอินเทอร์เน็ต)*
   - Performs NAT (Masquerade) to allow internal hosts to reach the simulated internet. *(ทำ NAT เพื่อให้เครื่องในวง LAN ออกเน็ตได้)*
   - Runs OSPF via FRRouting to exchange routes with R2. *(ใช้โปรโตคอล OSPF ร่วมกับ R2)*
2. **R2 (Internal Branch Router)**
   - Internal router that connects LAN B to the rest of the network via R1. *(เราเตอร์สาขา ทำหน้าที่เชื่อม LAN B ให้คุยกับวงอื่นและออกเน็ตผ่าน R1 ได้)*
   - Runs OSPF via FRR. *(รัน OSPF)*
3. **ServerA**
   - Python-based server inside LAN A. *(เซิร์ฟเวอร์ภาษา Python ในวง LAN A)*
4. **ServerB**
   - Python-based server inside LAN B. *(เซิร์ฟเวอร์ภาษา Python ในวง LAN B)*
5. **ClientA**
   - Simulated client machine in LAN A with networking tools pre-installed. *(เครื่องลูกข่ายสำหรับทดสอบในวง LAN A)*
6. **InternetTester**
   - Container sitting on the Internet network used to verify external connectivity. *(เครื่องที่จำลองเป็นเซิร์ฟเวอร์ปลายทางบนโลกอินเทอร์เน็ต)*

---

## ✨ Features Implemented (ฟีเจอร์หลัก)

- **Dynamic Routing (OSPF):** R1 and R2 use FRRouting (`frr.conf`) to dynamically advertise LAN A and LAN B routes. *(R1 และ R2 แลกเปลี่ยนเส้นทางกันได้อัตโนมัติ ไม่ต้องคอยเซ็ต Static Route เอง)*
- **NAT / Firewall:** Configured on R1 via `iptables` to translate LAN traffic. *(ตั้งค่าการแปลงไอพีและการกรองเส้นทางผ่าน iptables ไว้ที่ R1)*
- **IP SLA / Failover Monitoring:** Custom shell scripts (`ip_sla.sh`) are used to automatically detect interface or path failures and reroute traffic dynamically. *(มีสคริปต์ตรวจสอบความพร้อมของเส้นทาง หากเส้นทางไหนมีปัญหาก็จะปรับเปลี่ยนให้เอง)*
- **Automated Container Provisioning:** Uses custom `Dockerfile` builds and startup scripts to assign default routes. *(กำหนด Default Route ประจำคอนเทนเนอร์ให้อัตโนมัติเมื่อตอนสั่งรันด้วย Script)*

---

## 🚀 How to Run (วิธีเริ่มรันระบบ)

1. Ensure you have Docker and Docker Compose installed. *(เช็คให้แน่ใจว่าติดตั้ง Docker และ Docker Compose ในเครื่องเรียบร้อยแล้ว)*
2. Clone the repository and navigate to the project directory: *(จำลองการโคลนโปรเจกต์ลงเครื่อง)*
   ```bash
   git clone <repository_url>
   cd network-lab
   ```
3. Build and start the infrastructure: *(เริ่มรันตัวคอนเทนเนอร์และเซตอัพโครงสร้าง)*
   ```bash
   docker-compose up -d --build
   ```
4. Verify the containers are running: *(เช็คสถานะการทำงาน)*
   ```bash
   docker ps
   ```

---

## 🧪 Testing the Infrastructure (ชุดคำสั่งทดสอบแลป)

You can verify the connectivity by accessing the containers using `docker exec`:
*(หลังจากรันระบบเสร็จ สามารถก๊อปคำสั่งเหล่านี้ไปวางทดสอบการแชร์ของวงเครือข่ายและระบบ)*

**1. Test OSPF Routing (LAN A to LAN B):**
ตรวจสอบการสื่อสารแบบข้าม LAN ถ้าระบบ OSPF ทำงาน Client A จะต้องมองเห็น Server B ได้
```bash
docker exec -it ClientA ping 172.20.20.10
```

**2. Test NAT and Internet Access:**
Ping จากเครื่องลูกในวง LAN ออกไปสู่โลกอินเทอร์เน็ตภายนอก (ผ่าน R1NAT)
```bash
docker exec -it ClientA ping 172.30.0.100
```

**3. Check FRR Routing Tables on R1:**
ส่องดูตารางแสดงการค้นหาเส้นทางแบบอัตโนมัติบนตัวเราเตอร์หลัก (มองหาสัญลักษณ์ O ที่ย่อมาจาก OSPF)
```bash
docker exec -it R1 vtysh -c "show ip route"
```

## 📁 Project Structure (คำอธิบายโครงสร้างไฟล์)

- `/automation/`: Contains custom Dockerfiles, initialization scripts (`init.sh`), IP SLA health monitor scripts. *(เป็นที่เก็บโค้ดตั้งค่าและสคริปต์รันระบบพื้นฐาน)*
- `/config/`: Contains the FRR configuration files (`frr.conf`, `daemons`, `vtysh.conf`). *(โฟลเดอร์เก็บค่าคอนฟิกของเราเตอร์ R1 และ R2)*
- `docker-compose.yml`: The blueprint defining the networks, subnets, and container properties. *(ไฟล์หลักที่ใช้ระบุโครงสร้างการเชื่อมต่อทั้งหมดประหนึ่งสายแลนสมมติ)*
