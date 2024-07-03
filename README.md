# VXLAN_6to4

> This project is only for personal learning. Don't abuse.

# Setting Up a VXLAN Tunnel with Local IPv6

## مرحله 1: در ابتدا باید سرور ایران و خارج ما بتوانند از طریق IPv6 با یکدیگر ارتباط برقرار کنند

#### در این آموزش از تانل 6to4 برای گرفتن IPv6 لوکال استفاده شده، که خیلی سرعت بهتری نسبت به بقیه روش ها داره
#### این روش ممکنه در بعضی از سرور ها مسدود شده باشه که شما یا باید IP سرور خارجتون رو عوض کنید در غیر اینصورت میتونید با استفاده از IPv6 گلوبال سرورتون یا سایت تانل بروکر هم این تانل رو اجرا کنید.

### ابتدا این دستورات را داخل سرور ایران اجرا کنید :

```sh
ip tunnel add 6to4_To_KH mode sit remote <<KHAREJ-IPV4>>
ip -6 addr add fd00:155::1/64 dev 6to4_To_KH
ip link set 6to4_To_KH mtu 1480
ip link set 6to4_To_KH up
```


### سپس این دستورات را داخل سرور خارج اجرا کنید :
```sh
ip tunnel add 6to4_To_IR mode sit remote <<IRAN-IPV4>>
ip -6 addr add fd00:155::2/64 dev 6to4_To_IR
ip link set 6to4_To_IR mtu 1480
ip link set 6to4_To_IR up
```

>راهنمایی : (در قسمت `<IPv4-KHAREJ>` ، آیپی ورژن 4 پابلیک سرور خارج رو قرار میدیم و در بخش `<IPv4-IRAN>` ، آیپی ورژن 4 پابلیک ایران رو قرار میدیم)
