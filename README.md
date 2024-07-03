# VXLAN_6to4

> This project is only for personal learning. Don't abuse.

# Setting Up a VXLAN Tunnel with Local IPv6

## مرحله 1: در ابتدا باید سرور ایران و خارج ما بتوانند از طریق IPv6 با یکدیگر ارتباط برقرار کنند

#### در این آموزش از تانل 6to4 برای گرفتن IPv6 لوکال استفاده شده، که خیلی سرعت بهتری نسبت به بقیه روش ها داره
#### این روش ممکنه در بعضی از سرور ها مسدود شده باشه که شما یا باید IP سرور خارجتون رو عوض کنید در غیر اینصورت میتونید با استفاده از IPv6 گلوبال سرورتون یا سایت تانل بروکر هم این تانل رو اجرا کنید.


### برای شروع کار و اجرای تانل 6to4 از دستورات زیر شروع میکنیم:

>راهنمایی : (در قسمت `<<KHAREJ-IPV4>>` ، آیپی ورژن 4 پابلیک سرور خارج رو قرار میدیم و در بخش `<<IRAN-IPV4>>` ، آیپی ورژن 4 پابلیک ایران رو قرار میدیم)

#### دستورات سرور ایران :

```sh
ip tunnel add 6to4_To_KH mode sit remote <<KHAREJ-IPV4>>
ip -6 addr add fd00:155::1/64 dev 6to4_To_KH
ip link set 6to4_To_KH mtu 1480
ip link set 6to4_To_KH up
```


#### دستورات سرور خارج :
```sh
ip tunnel add 6to4_To_IR mode sit remote <<IRAN-IPV4>>
ip -6 addr add fd00:155::2/64 dev 6to4_To_IR
ip link set 6to4_To_IR mtu 1480
ip link set 6to4_To_IR up
```

#### برای اطمینان از اینکه تانل برقرار شده باشه وارد هر دو سرور بشید و از آیپی سرور مقابل پینگ بگیرید.
- به عنوان مثل وارد سرور ایران میشیم و این دستور رو برای پینگ گرفتن IPv6 استفاده میکنیم : 
```shell
ping6 fd00:155::2
```
- روی سرور خارچ نیز همین کار رو تکرار میکنیم :
```shell
ping6 fd00:155::1
```





## مرحله 2: ایجاد تانل VXLAN

### برای این کار در ابتدا باید پیش نیاز ها را روی هر دو سرور ایران و خارج نصب کنیم:
```shell
sudo apt update
sudo apt install iproute2
sudo apt-get install -y iptables-persistent
```

#### قبل از اینکه دستورات مربوط به تانل را بزنیم باید اسم شبکه را در هر سرور پیدا کنیم، برای اینکار از دستور زیر استفاده میکنیم:
>برای مثال نام شبکه من در سرور ایران `eth0` ، و در سرور خارج `ens3` است.

```shell
ls /sys/class/net/
```

### حالا دستورات مربوط به VXLAN رو اجرا میکنیم.

### توضیحات مهم:
- در انتهای خط اول دستورات اسم شبکه (ens3 و eth0) را با توجه به اسم شبکه سرور خود تغییر دهید.
- در این دستورات پورت تانل 53 است. شما میتوانید هر مقداری که خودتان دوست دارید قرار دهید.
- عدد VNI هر عددی میتواند باشد ولی باید در هر دو سرور یک مقدار باشد، (در اینجا مقدار 3188 قرار داده شده است).
- در این دستورات یک IPv4 لوکال روی اینترفیس VXLAN برای هر سرور در نظر گرفته شده است (به صورت پیشفرض با آدرس های 192.168.23.1 برای سرور ایران و 192.168.23.2 برای سرور خارج). این IP نیز میتواند هر مقدار دلخواهی باشد، فقط دقت کنید که قبلا در شبکه تعریف نشده باشد.
- بعد از اجرای دستورات اگر تانل به درستی برقرار باشد باید بتوانید از هر سرور IPv4 لوکال سرور مقابل را پینگ بگیرید. (از سرور ایران 192.168.23.2 را پینگ بگیرید و از سرور خارج 192.168.23.1 را پینگ بگیرید)


#### دستورات سرور ایران :

```sh
sudo ip link add vxlan0 type vxlan id 3188 dstport 53 local fd00:155::1 remote fd00:155::2 dev eth0
sudo ip link set vxlan0 mtu 1500
sudo ip link set vxlan0 up
sudo ip addr add 192.168.23.1/30 dev vxlan0
sudo iptables -A INPUT -p udp --dport 53 -j ACCEPT
sudo ip6tables -A INPUT -p udp --dport 53 -j ACCEPT
```


#### دستورات سرور خارج :
```sh
sudo ip link add vxlan0 type vxlan id 3188 dstport 53 local fd00:155::2 remote fd00:155::1 dev ens3
sudo ip link set vxlan0 mtu 1500
sudo ip link set vxlan0 up
sudo ip addr add 192.168.23.2/30 dev vxlan0
sudo iptables -A INPUT -p udp --dport 53 -j ACCEPT
sudo ip6tables -A INPUT -p udp --dport 53 -j ACCEPT
```
