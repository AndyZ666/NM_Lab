#!/usr/bin/env python3
import csv
import re
from netmiko import ConnectHandler

def read_ssh_info(csv_file):
    devices = {}
    with open(csv_file, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            devices[row["hostname"]] = {
                "device_type": "cisco_ios",
                "host": row["ip"],
                "username": row["username"],
                "password": row["password"],
                "timeout": 10,
            }
    return devices

def ssh_connect(device, command):
    try:
        with ConnectHandler(**device) as conn:
            output = conn.send_command(command)
            print(f"SSH connection established to {device['host']}")
            return output
    except Exception as e:
        return f"SSH connection failed: {device['host']} - {e}"

def get_r5_ipv6(r4):
    
    command = "show ipv6 neighbors"
    output = ssh_connect(r4, command)

    match = re.search(r"(2001:[0-9a-fA-F:]+)", output)
    if match:
        print(f"R5 IPv6 address obtained: {match.group(1)}")
        return match.group(1)
    else:
        print("Failed to obtain R5 IPv6 address!")
        return None

def configure_dhcp(r5):
   
    commands = [
        "ip dhcp excluded-address 10.0.1.1 10.0.1.10",
        "ip dhcp pool MYPOOL",
        "network 10.0.1.0 255.255.255.0",
        "default-router 10.0.1.1",
        "dns-server 8.8.8.8",
        "exit",
        "ip dhcp pool R2_STATIC",
        "host 10.0.1.2 255.255.255.0",
        "client-identifier 01:CA:02:0A:28:00:00",
        "exit",
        "ip dhcp pool R3_STATIC",
        "host 10.0.1.3 255.255.255.0",
        "client-identifier 01:CA:03:0A:47:00:00",
        "exit",
        "ip dhcp pool R4_STATIC",
        "host 10.0.1.1 255.255.255.0",
        "client-identifier 01:CA:04:0A:65:00:00",
        "exit"
    ]

    try:
        with ConnectHandler(**r5) as conn:
            print("Configuring DHCP on R5......")
            output = conn.send_config_set(commands)
            print("DHCP Configuration Success!")
            return output
    except Exception as e:
        print(f"Failed to configure DHCP: {e}")
        return None

def get_dhcp_bindings(r5):
    
    command = "show ip dhcp binding"
    output = ssh_connect(r5, command)
    ip_list = re.findall(r"(\d+\.\d+\.\d+\.\d+)", output)

    if ip_list:
        print(f"DHCP binding success! IPs: {ip_list}")
    else:
        print("NO DHCP bindings found!")
    return ip_list

if __name__ == "__main__":
    ssh_file = "sshInfo.csv"
    devices = read_ssh_info(ssh_file)

    r4 = devices.get("R4")
    r5 = devices.get("R5")

    if r4 and r5:
        r5_ipv6 = get_r5_ipv6(r4)
        if r5_ipv6:
            configure_dhcp(r5)
            dhcp_clients = get_dhcp_bindings(r5)
            print(f"DHCP binding IP addresses: {dhcp_clients}")
        else:
            print("Could not obtain R5 IPv6 address!")
    else:
        print("SSH connection failed!")
