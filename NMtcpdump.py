#!/usr/bin/env python3
from scapy.all import rdpcap, Ether, IP, ICMP

file = "capture1.pcap"
packets = rdpcap(file)

mac = {}

for pack in packets:
    if Ether in pack and IP in pack and ICMP in pack:
        src_mac = pack[Ether].src
        src_ip = pack[IP].src
        dst_ip = pack[IP].dst
        

        if pack[ICMP].type == 8 and src_ip.startswith("10.0.1.") and src_ip not in mac:
                mac[src_ip] = src_mac

print("Detected MAC Addresses of R2 and R3: ")
for ip, macadd in mac.items():
    print(f"IP: {ip} ----- MAC: {macadd}")