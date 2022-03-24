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

* Download iso file for last version of ubuntu ~~20.04~~ 16.04 LTS desktop (due to bug making ssd unaivalable in linux kermel > 5.11):
[ubuntu-16.04.7-desktop-amd64.iso](https://releases.ubuntu.com/xenial/ubuntu-16.04.7-desktop-amd64.iso)
* type in terminal ```sha256sum ubuntu-16.04.7-desktop-amd64.iso``` and verify that the provided code is the same as the one provided on ubuntu.com site (otherwise, means file was corrupted during download).

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

Start computer. You will arrive on grub menu to select system you want to boot on:
- default is linux ubuntu
- if you want to boot on windows, choose _Windows Manager_

Now you can boot on ubuntu 16.04.7 LTS

## Upgrade to ubuntu 20.04 LTS

