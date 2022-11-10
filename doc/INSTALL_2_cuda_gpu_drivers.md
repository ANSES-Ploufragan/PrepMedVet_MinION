# Instructions to install GPU drivers nvidia RTX3800 on a laptop running Ubuntu 20.04

Use the advised proprietary tested driver (510 for RTX3080 on ubuntu 20.04.6 LTS) using Ubuntu Graphical Software Installer.
> 510 drivers means CUDA 11.6

# Instructions to install CUDA (nvidia GPU computing) on a laptop running Ubuntu 20.04

Run in a command line:
```
sudo apt install nvidia-cuda-toolkit
```

> We did not use: ```sudo apt install cuda-drivers-fabricmanager-510```
