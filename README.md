# VXLAN_6to4

> This project is only for personal learning. Don't abuse.

**مرحله 1 : **
د.
در ضمن IPv6 لوکال استفاده شده در این آموزش سمپل هست و برای امنیت بیشتر میتونید خودتون یه آی پی یونیک از این سایت بگیرید: https://www.unique-local-ipv6.com/

# Setting Up a VXLAN Tunnel with Local IPv6

## Step 1: ر ابتدا باید سرور ایران و خارج ما بتوانند از طریق IPv6 با یکدیگر ارتباط برقرار کنند

### در این آموزش از تانل 6to4 برای گرفتن IPv6 لوکال استفاده شده، که خیلی سرعت بهتری نسبت به بقیه روش ها داره
ولی شما با استفاده از IPv6 گلوبال سرورتون یا سایت تانل بروکر هم میتونید این تانل رو اجرا کنید.

### Iran Server:

```sh
ip tunnel add 6to4_To_KH mode sit remote 139.185.48.39
ip -6 addr add fd00:155::1/64 dev 6to4_To_KH
ip link set 6to4_To_KH mtu 1480
ip link set 6to4_To_KH up
