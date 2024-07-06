# VXLAN_6to4_Tunnel

> This project is only for personal learning. Don't abuse.

# راه اندازی تانل VXLAN بین دو لینوکس با استفاده از IPv6

## مرحله 1: در ابتدا باید سرور ایران و خارج ما بتوانند از طریق IPv6 با یکدیگر ارتباط برقرار کنند

#### در این آموزش از تانل 6to4 برای گرفتن IPv6 لوکال استفاده شده، که خیلی سرعت بهتری نسبت به بقیه روش ها داره و نیازی هم نیست که سرور های شما IPv6 کلوبال داشته باشند.
#### تانل 6to4 ممکنه در بعضی از سرور ها مسدود شده باشه که شما باید IP سرور خارجتون رو عوض کنید.
#### با استفاده از IPv6 گلوبال سرورتون یا سایت تانل بروکر هم میتونید این تانل رو اجرا کنید که در این صورت این مرحله رو نادیده بگیرید.


### برای شروع کار و اجرای تانل 6to4 از دستورات زیر شروع میکنیم:

>راهنمایی : (در قسمت `<<KHAREJ-IPV4>>` ، آیپی ورژن 4 پابلیک سرور خارج رو قرار میدیم و در بخش `<<IRAN-IPV4>>` ، آیپی ورژن 4 پابلیک ایران رو قرار میدیم)

#### دستورات سرور ایران :

```sh
ip tunnel add 6to4_IN mode sit remote <<KHAREJ-IPV4>>
ip -6 addr add fd00:155::1/64 dev 6to4_IN
ip link set 6to4_IN mtu 1480
ip link set 6to4_IN up
```


#### دستورات سرور خارج :
```sh
ip tunnel add 6to4_OUT mode sit remote <<IRAN-IPV4>>
ip -6 addr add fd00:155::2/64 dev 6to4_OUT
ip link set 6to4_OUT mtu 1480
ip link set 6to4_OUT up
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

```shell
ls /sys/class/net/
```
>برای مثال نام شبکه من در سرور ایران `eth0` ، و در سرور خارج `ens3` است.

### حالا دستورات مربوط به VXLAN رو اجرا میکنیم.

### توضیحات مهم:
- در انتهای خط اول دستورات اسم شبکه (ens3 و eth0) را با توجه به اسم شبکه سرور خود تغییر دهید.
- در این دستورات پورت تانل 53 است. شما میتوانید هر مقداری که خودتان دوست دارید قرار دهید.
- عدد VNI هر عددی میتواند باشد ولی باید در هر دو سرور یک مقدار باشد، (در اینجا مقدار 3188 قرار داده شده است).
-  در اینجا IPv6 لوکال پیش فرض fd00:155::1 برای سرور ایران و fd00:155::2 برای سرور خارج قرار داده شده. شما با توجه به IPv6 که خودتون تو مرحله اول انتخاب کردید دستورات رو تغییر بدبد.
- در این دستورات یک IPv4 لوکال روی اینترفیس VXLAN برای هر سرور در نظر گرفته شده است (به صورت پیشفرض با آدرس های 192.168.23.1 برای سرور ایران و 192.168.23.2 برای سرور خارج). این IP نیز میتواند هر مقدار دلخواهی باشد، فقط دقت کنید که قبلا در شبکه تعریف نشده باشد.


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
- بعد از اجرای دستورات اگر ارتباط به درستی برقرار باشد باید بتوانید از هر سرور IPv4 لوکال سرور مقابل را پینگ بگیرید. (از سرور ایران 192.168.23.2 را پینگ بگیرید و از سرور خارج 192.168.23.1 را پینگ بگیرید)

## مرحله 3: هدایت ترافیک به سمت تانل:

### این بخش فقط در سرور ایران انجام می‌شود. به اینصورت که باید با فوروارد کردن ترافیک به سمت تانل به اینترنت دسترسی پیدا کنیم.

>نکته : اگر در مراحل قبل مقادیر `192.168.23.1` , `192.168.23.2` را تغییر دادید، باید اینجا هم دستورات را اصلاح کنید.
>
#### دستورات سرور ایران :

```sh
sysctl net.ipv4.ip_forward=1
iptables -t nat -A PREROUTING -p tcp --dport 22 -j DNAT --to-destination 192.168.23.1
iptables -t nat -A PREROUTING -j DNAT --to-destination 192.168.23.2
iptables -t nat -A POSTROUTING -j MASQUERADE
```

## ‌‌‌‌‌‌مرحله آخر: ذخیره کردن تانل و فعال سازی خودکار زمانی که سیستم ری استارت میشود
بعد از ریبوت شدن سرور دستورات پاک میشوند ، در صورت نیاز مینوانید از دستورات زیر استفاده کنید : 

**1. سرور ایران :**

- با دستور زیر فایل rc.local رو باز میکنیم 
```shell
sudo nano /etc/rc.local && sudo chmod +x /etc/rc.local
```

- متن زیر را در فایل قرار میدیم و فایل رو ذخیره میکنیم : 
```shell
#! /bin/bash
ip tunnel add 6to4_IN mode sit remote <<KHAREJ-IPV4>>
ip -6 addr add fd00:155::1/64 dev 6to4_IN
ip link set 6to4_IN mtu 1480
ip link set 6to4_IN up

sudo ip link add vxlan0 type vxlan id 3188 dstport 53 local fd00:155::1 remote fd00:155::2 dev eth0
sudo ip link set vxlan0 mtu 1500
sudo ip link set vxlan0 up
sudo ip addr add 192.168.23.1/30 dev vxlan0
sudo iptables -A INPUT -p udp --dport 53 -j ACCEPT
sudo ip6tables -A INPUT -p udp --dport 53 -j ACCEPT

sysctl net.ipv4.ip_forward=1
iptables -t nat -A PREROUTING -p tcp --dport 22 -j DNAT --to-destination 192.168.23.1
iptables -t nat -A PREROUTING -j DNAT --to-destination 192.168.23.2
iptables -t nat -A POSTROUTING -j MASQUERADE 

exit 0
```

**2. سرور خارج :**



- با دستور زیر فایل rc.local رو باز میکنیم 
```shell
sudo nano /etc/rc.local && sudo chmod +x /etc/rc.local
```

- متن زیر را در فایل قرار میدیم و فایل رو ذخیره میکنیم : 
```shell
#! /bin/bash
ip tunnel add 6to4_OUT mode sit remote <<IRAN-IPV4>>
ip -6 addr add fd00:155::2/64 dev 6to4_OUT
ip link set 6to4_OUT mtu 1480
ip link set 6to4_OUT up

sudo ip link add vxlan0 type vxlan id 3188 dstport 53 local fd00:155::2 remote fd00:155::1 dev ens3
sudo ip link set vxlan0 mtu 1500
sudo ip link set vxlan0 up
sudo ip addr add 192.168.23.2/30 dev vxlan0
sudo iptables -A INPUT -p udp --dport 53 -j ACCEPT
sudo ip6tables -A INPUT -p udp --dport 53 -j ACCEPT

exit 0
```

بعد از reboot کردن سیستم تغییرات اعمال خواهند شد.


## ‌‌‌‌‌‌نحوه تانل زدن یک Ubuntu خارج به روتر میکروتیک داخل ایران:

#### روی سرور خارج به جز دستورات بالا باید دستور زیر را نیز وارد کنیم: 
>مهم: اسم شبکه را باید با توجه به سرور خودتان تغییر دهید. در اینجا `ens3` است. (خط سوم)

```sh
echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward
sudo sysctl -w net.ipv4.ip_forward=1
sudo iptables -t nat -A POSTROUTING -o ens3 -j MASQUERADE
sudo sh -c "iptables-save > /etc/iptables/rules.v4"
```
#### داخل میکروتیک هم دستورات زیر را وارد کنید:


```sh
/interface vxlan add name=vxlan1 mtu=1500 vni=3188 dst-port=53 ipv6=yes local-address=fd00:155::1 remote-address=fd00:155::2
/interface vxlan set [find name=vxlan1] disabled=no
```
