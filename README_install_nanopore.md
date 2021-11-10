Installations instruction for __Ubuntu 18.04 LTS__

# Table of contents
1. [MinKNOW](#MinKNOW)
2. [guppy_gpu](#guppy-gpu)
3. [fast-bonito](#fast-bonito)
4. [bonito](#bonito)

# MinKNOW

## get repo

```
sudo apt-get update
sudo apt-get install wget
wget -O- https://mirror.oxfordnanoportal.com/apt/ont-repo.pub | sudo apt-key add -
echo "deb http://mirror.oxfordnanoportal.com/apt bionic-stable non-free" | sudo tee /etc/apt/sources.list.d/nanoporetech.sources.list
```

## Install MinKNOW:

```
sudo apt-get update
sudo apt-get install minion-nc

```

## Default installation directories

For the MinKNOW software:
/opt/ont/minknow

For the MinKNOW user interface:
/opt/ont/minknow-ui


## Location of the reads folder:

The reads folder is in /var/lib/minknow/data


## Location of the log files:

* The MinKNOW logs are located in /var/log/minknow
* The Guppy basecaller logs are located in /var/log/minknow/guppy


# guppy_gpu

> The GPU version (nvidia) of Guppy must be installed on the same system to which the MinION is connected

## Identify the version of the Guppy basecall server that MinKNOW is using:

```
/usr/bin/guppy_basecall_server --version
```

## Download the archive version of GPU-enabled Guppy from the Nanopore Community.

The specific URL to use is:

https://mirror.oxfordnanoportal.com/software/analysis/ont-guppy_<version>_linux64.tar.gz

Where <version> is the numeric part (major.minor.patch) obtained from the step above.

Example:
https://mirror.oxfordnanoportal.com/software/analysis/ont-guppy_3.2.10_linux64.tar.gz

> Note that the version of Guppy must match the version packaged within MinKNOW to prevent errors. 

## Extract the archive to a folder.

Example:
tar -C /home/myuser/ont-guppy -xf ont-guppy_XXX_linux64.tar.gz

## Use systemctl to edit the existing guppyd service (this will open a text editor with a copy of the existing service file):

```
sudo systemctl edit guppyd.service --full
```

## Edit that new service file to point to your GPU version of Guppy, and add the appropriate device flag. You can change any other server arguments at the same time.

For example, change this line in the service file:

```
ExecStart=/opt/ont/guppy/bin/guppy_basecall_server <things>
```

...to this (make sure you retain the "--port" argument exactly as it used to be -- this is how MinKNOW communicates with the basecall server):

```
ExecStart=/home/myuser/ont-guppy/bin/guppy_basecall_server <things> -x cuda:all
```

## Save the file and exit the text editor (the filename may look odd, but systemctl should change it to the correct name later).


## Stop the guppyd service:

```
sudo service guppyd stop
```

Confirm the guppy_basecall_server process is not running:

```
ps -A | grep guppy_basecall_
```

If the result of the above command is not blank, manually kill the process:

```
sudo killall guppy_basecall_server
```

## Start the guppyd service:

```
sudo service guppyd start
```

## Confirm the guppy_basecall_server is running and is using the GPU:

```nvidia-smi```


> If the guppy_basecall_server is not launching correctly, check its log output using journalctl ("-n 100" shows the last 100 entries in the journal) to see what is going wrong:

```
sudo journalctl -u guppyd.service -n 100
```

## Start the MinKNOW service:

```
sudo service minknow start
```

## TroubleShooting


### Check the Guppy basecall server logs.

Guppy log files are stored in /var/log/guppy

### Use journalctl to directly read the log entries produced by guppy and systemctl:

```
sudo journalctl -u guppyd.service -n 100
```

### Check whether the service is enabled.

```
systemctl list-unit-files | grep guppyd.service
```


If the service is not listed as "enabled", then it will either be marked as "disabled" or "masked". You can reset those statuses as described below.

* If the service is marked as "disabled":

```
sudo systemctl enable guppyd.service
```


* If the service is marked as "masked":

```
sudo systemctl unmask guppyd.service
```

You may then need to enable the service as described above.

### Reinstall the service.

```
sudo apt install --reinstall ont-guppyd-for-minion
sudo systemctl revert guppyd.service
sudo service guppyd restart
```

### Setting GPU parameters for lower-memory graphics cards.

When using GPUs with 8 GB of memory or less, larger basecall models (such as HAC and Sup) may not run. In this case it is recommended to lower the chunks_per_runner parameter of the basecall server to reduce memory use. This parameter is set when launching the basecall server.

Edit the guppyd service file and add --chunks_per_runner <value> to the ExecStart line, before restarting the service.

The following settings are recommended for 8 GB graphics cards. For cards with less GPU memory, or if the GPU is being used by other processes, these numbers may need to be lowered.

* For HAC or modified basecalling models, use --chunks_per_runner 160
* For Sup basecalling models, use --chunks_per_runner 10



# fast-bonito

Download of env_gpu.yml from https://github.com/EIHealth-Lab/fast-bonito.git

```
# Setup environment using conda
conda env create -f env_gpu.yml 
conda env update -f env_gpu.yml
source activate fast-bonito

# Install fast-bonito
git clone https://github.com/EIHealth-Lab/fast-bonito.git
cd fast-bonito
python setup.py install
```

* Error message obtained for first test:
* __solved__ by __adding__ at just before the fast-bonito command in bash script (can be set at the end of __~/.bashrc__):  
```ulimit -n 4096```

# bonito

from [github](https://github.com/nanoporetech/bonito)

```
sudo apt install pkg-config libhdf5-dev
pip install -f https://download.pytorch.org/whl/torch_stable.html ont-bonito-cuda111
bonito download --models --latest -f
```

> bonito models are also used by fast-bonito
