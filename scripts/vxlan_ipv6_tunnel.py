import subprocess
import configparser
import os

def run_command(command):
    """
    اجرای یک دستور در shell و بازگشت خروجی آن.
    """
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error while executing command: {command}\nError: {e.stderr}")
        raise

def get_network_interfaces():
    """
    دریافت لیست اینترفیس‌های شبکه
    """
    return os.listdir('/sys/class/net/')

def configure_ipv6_tunnel(remote_ip, local_ipv6):
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

def load_config(config_file):
    """
    بارگذاری پیکربندی از فایل ini.
    """
    config = configparser.ConfigParser()
    config.read(config_file)
    return config
