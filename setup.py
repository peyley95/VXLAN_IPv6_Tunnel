import os
import sys
from scripts.vxlan_ipv6_tunnel import (
    install_prerequisites,
    configure_ipv6_tunnel,
    configure_vxlan,
    get_network_interfaces,
    load_config,
)

def main():
    # بارگذاری پیکربندی از فایل ini
    config_file = os.path.join(os.path.dirname(__file__), 'config', 'config.ini')
    config = load_config(config_file)

    # نصب پیش‌نیازها
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
        # اجرای پیکربندی 6to4 با استفاده از مقادیر پیکربندی
        remote_ip = config['6to4']['remote_ip']
        local_ipv6 = config['6to4']['local_ipv6']
        configure_ipv6_tunnel(remote_ip, local_ipv6)
        print("IPv6 tunnel configured. Test connectivity with ping6.")
        
    elif choice == '2':
        # اجرای پیکربندی VXLAN با استفاده از مقادیر پیکربندی
        vxlan_id = config['vxlan']['vxlan_id']
        dst_port = config['vxlan']['dst_port']
        local_ipv6 = config['vxlan']['local_ipv6']
        remote_ipv6 = config['vxlan']['remote_ipv6']
        local_ipv4 = config['vxlan']['local_ipv4']
        configure_vxlan(vxlan_id, dst_port, local_ipv6, remote_ipv6, local_ipv4, interface_name)
        print("VXLAN tunnel configured. Test connectivity by pinging the remote IPv4.")
        
    else:
        print("Invalid choice. Exiting.")
        sys.exit(1)

if __name__ == "__main__":
    main()
