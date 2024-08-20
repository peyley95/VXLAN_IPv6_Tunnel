import subprocess
import os
import sys

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error while executing command: {command}\nError: {e.stderr}")
        sys.exit(1)

def get_network_interfaces():
    """
    دریافت لیست اینترفیس‌های شبکه
    """
    return os.listdir('/sys/class/net/')

def configure_ipv6_tunnel(remote_ip, local_ipv6, interface_name):
    """
    پیکربندی تونل 6to4 برای IPv6 لوکال.
    """
    print("Configuring 6to4 tunnel for IPv6...")
    run_command(f"ip tunnel add 6to4_IN mode sit remote {remote_ip}")
    run_command(f"ip -6 addr add {local_ipv6}/64 dev 6to4_IN")
    run_command("ip link set 6to4_IN mtu 1480")
    run_command("ip link set 6to4_IN up")

def configure_vxlan(vxlan_id, dst_port, local_ipv6, remote_ipv6, local_ipv4, interface_name):
    """
    پیکربندی تانل VXLAN.
    """
    print("Configuring VXLAN tunnel...")
    run_command(f"sudo ip link add vxlan0 type vxlan id {vxlan_id} dstport {dst_port} local {local_ipv6} remote {remote_ipv6} dev {interface_name}")
    run_command("sudo ip link set vxlan0 mtu 1280")
    run_command("sudo ip link set vxlan0 up")
    run_command(f"sudo ip addr add {local_ipv4} dev vxlan0")
    run_command(f"sudo iptables -A INPUT -p udp --dport {dst_port} -j ACCEPT")
    run_command(f"sudo ip6tables -A INPUT -p udp --dport {dst_port} -j ACCEPT")

def install_prerequisites():
    """
    نصب پیش‌نیازهای مورد نیاز.
    """
    print("Installing prerequisites...")
    run_command("sudo apt update")
    run_command("sudo apt install -y iproute2")
    run_command("sudo apt-get install -y iptables-persistent")

def main():
    """
    تابع اصلی برای مدیریت انتخاب‌ها و اجرای مراحل.
    """
    install_prerequisites()
    
    # انتخاب اینترفیس شبکه
    interfaces = get_network_interfaces()
    print(f"Available network interfaces: {', '.join(interfaces)}")
    interface_name = input("Enter the network interface name you want to use: ")

    if interface_name not in interfaces:
        print(f"Interface {interface_name} not found!")
        sys.exit(1)

    choice = input("Do you want to (1) configure 6to4 tunnel for local IPv6 or (2) setup VXLAN tunnel? Enter 1 or 2: ")

    if choice == '1':
        remote_ip = input("Enter the remote IPv4 address (e.g., <KHAREJ-IPV4>): ")
        local_ipv6 = input("Enter the local IPv6 address you want to assign (e.g., fd00:155::1): ")
        configure_ipv6_tunnel(remote_ip, local_ipv6, interface_name)
        print("IPv6 tunnel configured. Test connectivity with ping6.")
        
    elif choice == '2':
        vxlan_id = input("Enter VXLAN ID (e.g., 3188): ")
        dst_port = input("Enter VXLAN port (default is 53): ")
        local_ipv6 = input("Enter the local IPv6 address (e.g., fd00:155::1): ")
        remote_ipv6 = input("Enter the remote IPv6 address (e.g., fd00:155::2): ")
        local_ipv4 = input("Enter the local IPv4 address for VXLAN (e.g., 192.168.23.1/30): ")
        configure_vxlan(vxlan_id, dst_port, local_ipv6, remote_ipv6, local_ipv4, interface_name)
        print("VXLAN tunnel configured. Test connectivity by pinging the remote IPv4.")
        
    else:
        print("Invalid choice. Exiting.")
        sys.exit(1)

if __name__ == "__main__":
    main()
