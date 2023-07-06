
[[_TOC_]]

# Instructions to install GPU drivers nvidia RTX3800 on a laptop running Ubuntu 20.04

Use the advised proprietary tested driver (510 for RTX3080 on ubuntu 20.04.6 LTS) using Ubuntu Graphical Software Installer.
> 510 drivers means CUDA 11.6

# Instructions to install CUDA (nvidia GPU computing) on a laptop running Ubuntu 20.04

Run in a command line:
```
sudo apt install nvidia-cuda-toolkit
```

> We did not use: ```sudo apt install cuda-drivers-fabricmanager-510```

# page of CUDA / drivers compatibilities

[cuda-toolkit-release-notes](https://docs.nvidia.com/cuda/cuda-toolkit-release-notes/index.html)

# Updates

* When you update/upgrade ubuntu, you may have different nvidia/cuda drivers updated

* Currently guppy_gpu is __supporting CUDA 11.8__, __not CUDA 12__
* To downgrade CUDA to CUDA 11.8, do this:

  - remove current nvidia/cuda drivers: 
```
sudo apt-get --purge remove "*cublas*" "*cufft*" "*curand*" "*cusolver*" "*cusparse*" "*npp*" "*nvjpeg*" "cuda*" "nsight*" 
```

  - install CUDA 11.8, fiting driver will be installed automatically during the process:
  > obtained from [cuda-11-8-0 for Ubuntu 20.04 LTS](https://developer.nvidia.com/cuda-11-8-0-download-archive?target_os=Linux&target_arch=x86_64&Distribution=Ubuntu&target_version=20.04&target_type=deb_local)
```
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin
sudo mv cuda-ubuntu2004.pin /etc/apt/preferences.d/cuda-repository-pin-600
wget https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda-repo-ubuntu2004-11-8-local_11.8.0-520.61.05-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu2004-11-8-local_11.8.0-520.61.05-1_amd64.deb
sudo cp /var/cuda-repo-ubuntu2004-11-8-local/cuda-*-keyring.gpg /usr/share/keyrings/
sudo apt-get updatesudo apt-get -y install cuda

```
