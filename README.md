# Laboratorio de Seguridad: Ataque MitM mediante DHCP Spoofing

**Autor:** Wilfri Solano Frias  
**Matrícula:** 2024-2364   

-------------------------------------------------------------------------------------------------------------------------

## 1. Objetivo del Laboratorio
Conocer las vulnerabilidades y peligros reales de los entornos LAN cuando los conmutadores permiten la libre inyección de paquetes de control por parte de puertos de usuario no autorizados, analizando cómo un atacante puede suplantar la identidad de servicios críticos y desviar el tráfico de datos de la red.

-------------------------------------------------------------------------------------------------------------------------

## 2. Objetivo del Script
Configurar un demonio de escucha pasiva (Sniffer) que capture las solicitudes DHCP legítimas (Discover y Request) de la red e inyecte de forma inmediata respuestas falsas (DHCP Offer y DHCP Ack) para forzar a la víctima a usar al atacante como su servidor y puerta de enlace predeterminada.

### 2.1. Requisitos para utilizar la herramienta
* **Sistema Operativo:** Kali Linux.
* **Lenguaje:** Python 3.x.
* **Librerías/Dependencias:** Scapy. Instalar el entorno de red con: `pip install scapy`.
* **Entorno de Red:** La interfaz `eth0` debe residir en el mismo dominio de difusión (VLAN 1) de los hosts bajo prueba para capturar las peticiones de broadcast por el puerto UDP 67, en modo promiscuo y con privilegios de administrador (root).

### 2.2. Parámetros Usados
El script admite y manipula las siguientes variables globales y configuraciones:

**Variables Globales del Atacante (Líneas 4-6)**
* `INTERFACE = "eth0"`: Enlaza el socket crudo al adaptador virtual activo de la estación de ataque.
* `ATTACKER_MAC = "02:00:11:22:33:44"`: MAC ficticia que el switch registrará como el servidor de origen de las respuestas.
* `FAKE_SERVER_IP = "192.168.1.254"`: IP del Gateway falso utilizado para efectuar el desvío MitM (Man-in-the-Middle).

**Variables Globales de Red (Líneas 7-9)**
* `VICTIM_ASSIGNED_IP = "192.168.1.150"`: Dirección IP maliciosa destinada a ser inyectada en la máquina víctima.
* `NETMASK = "255.255.255.0"`: Máscara de red forzada por el script para mantener la coherencia de la subred.
* `DNS_SERVER = "8.8.8.8"`: Servidor DNS entregado a la víctima para asegurar que resuelva nombres y no sospeche del ataque al navegar.

-------------------------------------------------------------------------------------------------------------------------

## 3. Documentación del Funcionamiento del Script
Cuando el host Windows 10 inicia su solicitud de red enviando un paquete *DHCP Discover* vía Broadcast, el switch SWI2 replica la trama hacia todos los puertos del dominio de difusión. El script captura el paquete mediante la función `sniff()` filtrando el tráfico del puerto UDP 67, extrae su identificador de transacción (`xid`) y valida el tipo de mensaje. 

Si es un *Discover* (tipo 1), inyecta de forma inmediata una respuesta *DHCP Offer* maliciosa simulando ser el servidor legítimo. En cuanto el cliente responde con un *DHCP Request* (tipo 3) para aceptar los datos, el script intercepta nuevamente la trama e inyecta un paquete *DHCP Ack* falso. El switch conmuta estas tramas de regreso hacia el puerto `Ethernet0/2`, provocando que Windows 10 asuma la IP `.150` y configure la IP del atacante (`.254`) como su Default Gateway, completando la suplantación.

-------------------------------------------------------------------------------------------------------------------------

## 4. Documentación de la Red

### 4.1. Topología
* **Descripción:** Infraestructura en GNS3 distribuida para interceptar y alterar la asignación dinámica de direccionamiento lógico mediante el control de la capa de enlace.
* **VLANs Configuradas:** VLAN 1 (Nativa / Por defecto).
* **Direccionamiento IP:**
  * **Segmento de Red:** `192.168.64.0` / `255.255.255.0`
  * **Router de Laboratorio (Servidor DHCP legítimo):** Configurado originalmente en la IP `.1`.
  * **Estación Atacante (Kali Linux):** IP estática `192.168.64.23` (Interface `eth0`).
  * **Víctima (Windows 10):** Host de acceso que recibe de manera forzada la IP `192.168.1.150`.
* **Interfaces Clave (SWI2 - Cisco IOU Layer 2):**
  * `Ethernet0/0`: Conectado hacia el Router legítimo.
  * `Ethernet0/1`: Conectado a la estación del atacante Kali Linux.
  * `Ethernet0/2`: Conectado a la víctima Windows 10.

-------------------------------------------------------------------------------------------------------------------------

## 5. Contramedidas (Mitigación)

### 5.1 Implementación de DHCP Snooping (Mitigación Definitiva en la Red)
Para bloquear este ataque de forma automatizada desde la infraestructura de red, se implementó DHCP Snooping en el switch. Esta característica actúa como un cortafuegos de Capa 2, clasificando los puertos en "Confiables" (*Trusted*) y "No Confiables" (*Untrusted*). Las respuestas DHCP (*Offer/Ack*) procedentes de puertos *Untrusted* se descartan inmediatamente.


SWI2# configure terminal
SWI2(config)# ip dhcp snooping
SWI2(config)# ip dhcp snooping vlan 1
SWI2(config)# interface Ethernet0/0
SWI2(config-if)# ip dhcp snooping trust

-------------------------------------------------------------------------------------------------------------------------

## 6. Evidencias

### 6.1. Demostración en Video
En el siguiente enlace se encuentra el video demostrativo donde se visualiza la topología con la ejecución del ataque y la aplicación de la contramedida: 

https://www.youtube.com/watch?v=UtyPoIAu-VY&list=PLGfNWxn7Di3BhsEEifmTJKXP4_U9fla7P&index=2

### 6.2. Capturas de Pantalla

**A. Diseño de la Topología en GNS3**

<img width="715" height="522" alt="imagen" src="https://github.com/user-attachments/assets/8b27957e-4962-43e4-9718-66ac57b56b5d" />

**B. Captura de Asignación en el Host** 

<img width="581" height="206" alt="imagen" src="https://github.com/user-attachments/assets/7efb916e-3beb-4888-bbf9-b269c7b0e4b9" />

**C. Ejecución del Script en Kali Linux** 

<img width="625" height="90" alt="imagen" src="https://github.com/user-attachments/assets/ee7abe69-6c27-4cdd-8852-c24d66c6c10b" />

**D. Captura del Host Víctima comprometida** 

<img width="532" height="206" alt="imagen" src="https://github.com/user-attachments/assets/677e31aa-b71e-44d7-a57f-6904806991c1" />

**E. Aplicación de Contramedidas (DHCP Snooping Activo)** 

<img width="323" height="206" alt="imagen" src="https://github.com/user-attachments/assets/4716fe46-2d1d-48e8-baf3-ad802297b852" />

<img width="421" height="38" alt="imagen" src="https://github.com/user-attachments/assets/26bcaaa0-1f9c-467b-8d5f-93122452edb2" />
