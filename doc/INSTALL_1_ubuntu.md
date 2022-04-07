# Intructions to install Ubuntu 20.04 on a laptop MSI GS66 Stealth (core i9, RTX3080, 64 GB RAM, 2 TB nvme Samsung ssd)

## computer preparation

Go to BIOS (__Supp__ button pushed during boot):
- disable __secure boot__ in boot section
- change boot order to have:
  1: USB CD/DVD
  2: USB Hard Disk
  3: Windows Manager
  (...)
- in Boot->UEFI Hard Disk BBS Priorities, you must have _Windows Manager_
- F10 to save and exit

In windows 10:
- Right clic on "Start Up"->"Manadge Discs"
- Select Windows partition. Clic on "Action"->"Reduct the volume" and let 10 GB more than the minimal asked Windows portion.
  (it allows to prepare space for futur linux partition(s))
- Clic on "File"->"Quit"


## bootable usb device preparation

* Download iso file for last version of ubuntu ~~20.04~~ 18.04.6 LTS desktop (due to bug making ssd unaivalable in linux kermel > 5.11):
[ubuntu-18.04.6-desktop-amd64.iso](https://releases.ubuntu.com/xenial/ubuntu-18.04.6-desktop-amd64.iso)
* type in terminal ```sha256sum ubuntu-18.04.6-desktop-amd64.iso``` and verify that the provided code is the same as the one provided on ubuntu.com site (otherwise, means file was corrupted during download).

Create a bootable key using this iso file:
- on ubuntu:  StartUpDiskCreator (selecting the downloaded iso linux image and the USB key you will use to boot (>= 16 GB))
- on windows 10: (balena)-Etcher

## installation

* Start computer stay pressing F10, and choose the USB key to boot.
* Follows the instructions for an __installation alongside Windows Manager__
* The installer tells you it modifies two partitions (not yet existing, it creates it in the space let by Windows when we reduced its Volume.
* Finish the process.
* Switch off ubuntu (clic on top roght hand corner->Power off, confirm when asked)

> Linux is installed but the computer will boot on windows because Windows Manager is prioritary. We are going to change boot priority in the BIOS

## changing boot priority

Go to BIOS (__Supp__ button pushed during boot):
- in Boot->UEFI Hard Disk BBS Priorities, you must select:
  - Hard Disk:ubuntu (SAMSUNG...)
- changeed boot order must be now:
  1: USB CD/DVD
  2: USB Hard Disk
  3: Hard Disk:ubuntu (SAMSUNG...)
  (...)
- F10 to save and exit

Switch off computer

## Start

### Install ubuntu 18.04.6 LTS

Start computer. You will arrive on grub menu to select system you want to boot on:
- default is linux ubuntu
- if you want to boot on windows, choose _Windows Manager_

Now you can boot on ubuntu 18.04.6 LTS.

But network interfaces are not available (neither ethernet nor wifi).

### Configure network interface (wifi)

# Manual installation of drivers based on instructions at the bottom of [this page](https://askubuntu.com/questions/1299842/no-wifi-and-ethernet-connection-on-msi-gaming-edge-wifi-where-and-how-do-i-inst) whose interesting commands are reported here

## Equivalent of __Download the Latest Git and Build-Essential packages__:

* download on another computer of the following packages for ubuntu 18.04 LTS:
  - ethtools (pour outils de diagnostic/visualisation)
  - net-tools (pour outils de diagnostic/visualisation)

  - libdpkg-perl
  - dpkg-dev
  - build-essential
  - libc6
  - libc6-dev
  - libc-dev-bin
  - libcilkrts
  - libubsan
  - g++-7 
  - gcc 
  - gcc-7 
  - libasan 
  - libatomic1 
  - libcilkrts5 
  - libgcc-7-dev 
  - libitm1 
  - liblsan0 
  - libmpx2 
  - libquadmath0 
  - libstdc++-7-dev 
  - libtsan0 
  - libubsan0
  - g++
  - make

(list of deb:
```
build-essential_12.4ubuntu1_amd64.deb      libc6_2.27-3ubuntu1.5_amd64.deb              libmpx2_8.4.0-1ubuntu1_18.04_amd64.deb
dpkg-dev_1.19.0.5ubuntu2_all.deb           libc6-dev_2.27-3ubuntu1.5_amd64.deb          libquadmath0_8.4.0-1ubuntu1_18.04_amd64.deb
g++_7.4.0-1ubuntu2.3_amd64.deb             libc-dev-bin_2.27-3ubuntu1.5_amd64.deb       libstdc++-7-dev_7.5.0-3ubuntu1_18.04_amd64.deb
g++-7_7.5.0-3ubuntu1_18.04_amd64.deb       libcilkrts5_7.5.0-3ubuntu1_18.04_amd64.deb   libtsan0_8.4.0-1ubuntu1_18.04_amd64.deb
gcc_7.4.0-1ubuntu2.3_amd64.deb             libdpkg-perl_1.19.0.5ubuntu2_all.deb         libubsan0_7.5.0-3ubuntu1_18.04_amd64.deb
gcc-7_7.5.0-3ubuntu1_18.04_amd64.deb       libgcc-7-dev_7.5.0-3ubuntu1_18.04_amd64.deb  linux-libc-dev_4.15.0-173.182_amd64.deb
libasan4_7.5.0-3ubuntu1_18.04_amd64.deb    libitm1_8.4.0-1ubuntu1_18.04_amd64.deb       make_4.1-9.1ubuntu1_amd64.deb
```
)

with for each (or foreach group of files, the main programs being g++, make, build-essential), the command
```
sudo apt install ./my_file.deb
```

## Search for involved drivers

* Material
  - Killer E3100G Intel (drivers Windows 10 dispo en janvier 2022)
  - Killer(R) Wifi 6E AX1675x Intel (drivers Windows 10 dispo en janvier 2022)

* Activation of Intel drivers
```
sudo modprobe -a iwlwifi
```

* Inactivation of the Realtek drivers selected by defaut:
```
sudo modprobe -r r8169
```

Add in ```/etc/modprobe.d/blacklist.conf``` of
```
# avoid realtek drivers
blacklist r8169
```


No relevant result (except a visible interface not working, we had none before that).


## Equivalent de __Download the Iwlwifi-Firmware.git repository__: 

* On another linux computer:
```
git clone git://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git
```
compression, copy on a USB key and uncompression on the laptop (to avoid error of link copies), then
```
cd linux-firmware
sudo cp iwlwifi-* /lib/firmware/
cd ..
```

## Equivalent to __Create the Backported Iwlwifi Driver for your current setup__:

* On another linux computer:
```
git clone https://git.kernel.org/pub/scm/linux/kernel/git/iwlwifi/backport-iwlwifi.git
```
compression, copy on USB key and uncompression on laptop (to avoid error of link copies), then
```
cd backport-iwlwifi
sudo make defconfig-iwlwifi-public
sudo make -j4
sudo make install
update-initramfs -u
```

* make the wifi network visible (in the graphical interface)

ifconfig donne

# update et upgrade de ubuntu 18.04 sur connexion wifi

```
sudo apt update
sudo apt upgrade
```

> Note: la __mise à jour casse le réseau créé__. Il faut reprendre à partir de la compilation (dans backport... faire un make clean puis repartir d'un dossier tout propre fraichement dézippé et refaire toute la manip à partir de __Download the Iwlwifi-Firmware.git repository__)  suivi des commandes __modprobe__ de sélection de drivers intel et de suppression de drivers realtek,

* Result of ```ifconfig``` with wifi network working:

```
lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        inet6 ::1  prefixlen 128  scopeid 0x10<host>
        loop  txqueuelen 1000  (Boucle locale)
        RX packets 3626  bytes 263151 (263.1 KB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 3626  bytes 263151 (263.1 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

wlp48s0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 172.20.10.11  netmask 255.255.255.240  broadcast 172.20.10.15
        inet6 2a04:cec0:10e5:2a84:7c73:cb60:4a80:2fe8  prefixlen 64  scopeid 0x0<global>
        inet6 2a04:cec0:10e5:2a84:f342:20df:f46:a7f9  prefixlen 64  scopeid 0x0<global>
        inet6 fe80::c97b:5655:ee93:414f  prefixlen 64  scopeid 0x20<link>
        ether 4c:77:cb:1e:d4:21  txqueuelen 1000  (Ethernet)
        RX packets 417318  bytes 568108598 (568.1 MB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 230810  bytes 22561279 (22.5 MB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```

The wifi network is on but not the ethernet network, explanation found here:
```
2e:00.0 Ethernet controller [0200]: Realtek Semiconductor Co., Ltd. Device [10ec:3000] (rev 06)
	Subsystem: Micro-Star International Co., Ltd. [MSI] Device [1462:12f5]
	Kernel modules: r8169
30:00.0 Network controller [0280]: Intel Corporation Device [8086:2725] (rev 1a)
	Subsystem: Bigfoot Networks, Inc. Device [1a56:1674]
	Kernel driver in use: iwlwifi
	Kernel modules: iwlwifi
```
Le Realtek driver is boring...


### do release upgrade to ubuntu 20.04 LTS

```sudo do-release-upgrade```

Rerun __update et upgrade de ubuntu 18.04 sur connexion wifi__ to rescue wifi network.

### Upgrade kernel

(because black screen with nvidia drivers at boot are due to kernel incompatibility with very recent intel processors.
Everythong tells the drivers and grpagic cards are ok, but if you do, you get a black screen at boot).

Solution: update kernel as explained [here](https://forums.developer.nvidia.com/t/ubuntu-20-04-with-kernel-5-13-0-30-generic-doesnt-recognize-rtx-3080-ti-laptop-gpu/204433/3)
with [this repo](https://launchpad.net/%7Edamentz/+archive/ubuntu/liquorix) and installing [this way](https://liquorix.net/#install), summarized:

```
sudo add-apt-repository ppa:damentz/liquorix
sudo apt-get update
sudo apt-get install linux-image-liquorix-amd64 linux-headers-liquorix-amd64
```
Then reboot 

# select drivers to install in the graphical interface

* For the RTX3080 laptop, we need 510 drivers as explained [here](https://www.nvidia.com/fr-fr/geforce/drivers/) après renseignement des informations.
I selected advised  ```NVIDIA driver metapackage depuis nvidia-driver-510 (propriétaire, testé)```
and  clicked on "Apply"

Then in a terminal, write:
```
sudo prime-select nvidia
```



### Desactivate hibernation

```sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target```



