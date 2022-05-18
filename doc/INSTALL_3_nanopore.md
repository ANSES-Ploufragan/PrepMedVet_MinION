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
echo "deb http://mirror.oxfordnanoportal.com/apt focal-stable non-free" | sudo tee /etc/apt/sources.list.d/nanoporetech.sources.list
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

## For proxy

 If you have a proxy server and would like to set up MinKNOW using a proxy, follow the instructions below.

Open the user conf file ```/opt/ont/minknow/conf/user_conf```
and edit the following portion of the file:

```
"proxy": {
"cereal_class_version": 0,
"use_system_settings": true,
"auto_detect": true,
"auto_config_script": "",
"https_proxy": "",
"proxy_bypass": ""
```

Edit the https_proxy setting, which should be in the style of:

scheme://[username:password@]host:port or "http://domain\\username:password@host:port", where "scheme" is one of https, socks, socks4 or socks5.



# guppy_gpu

> The GPU version (nvidia) of Guppy must be installed on the same system to which the MinION is connected


## 1. Add Oxford Nanopore's deb repository to your system (this is to install Oxford Nanopore Technologies-specific dependency packages):

```
sudo apt-get update
sudo apt-get install wget lsb-release
export PLATFORM=$(lsb_release -cs)
wget -O- https://mirror.oxfordnanoportal.com/apt/ont-repo.pub | sudo apt-key add -
echo "deb http://mirror.oxfordnanoportal.com/apt ${PLATFORM}-stable non-free" | sudo tee /etc/apt/sources.list.d/nanoporetech.sources.list
sudo apt-get update
```



## 2. To install the .deb for Guppy, use the following command:

```
sudo apt update
sudo apt install ont-guppy --no-install-recommends
```

This will install the GPU version of Guppy.

## Rename the existing override.conf file so that it does not override our new settings:

```
sudo mv /etc/systemd/system/guppyd.service.d/override.conf /etc/systemd/system/guppyd.service.d/override.conf.old
```

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


## Stop the MinKNOW service:

```
sudo service minkown stop
```

## Stop the guppyd service:

```
sudo service guppyd stop
```

* Confirm the guppy_basecall_server process is not running:

```
ps -A | grep guppy_basecall_
```

* If the result of the above command is not blank, manually kill the process:

```
sudo killall guppy_basecall_server
```

## Start the guppyd service:

```
sudo service guppyd start
```

## Confirm the guppy_basecall_server is running and is using the GPU:

``` 
nvidia-smi
``` 

> If the guppy_basecall_server is not launching correctly, check its log output 
using journalctl ("-n 100" shows the last 100 entries in the journal) to see 
what is going wrong:

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


### Setting GPU parameters for lower-memory graphics cards.

When using GPUs with 8 GB of memory or less, larger basecall models (such as HAC and Sup) may not run. In this case it is recommended to lower the chunks_per_runner parameter of the basecall server to reduce memory use. This parameter is set when launching the basecall server.

Edit the guppyd service file and add --chunks_per_runner <value> to the ExecStart line, before restarting the service.

The following settings are recommended for 8 GB graphics cards. For cards with less GPU memory, or if the GPU is being used by other processes, these numbers may need to be lowered.

* For HAC or modified basecalling models, use --chunks_per_runner 160
* For Sup basecalling models, use --chunks_per_runner 10

### Performance guppy GPU setup

According to [this blog](https://hackmd.io/@Miles/B1U-cOMyu):

- the __fast__ model is tuned to deliver an optimised accuracy while being efficient (keeping up with data generation).
- the __high accuracy__ (HAC) model provides higher consensus/raw read accuracy over the fast model. However it is __5-8 times slower__ than the __fast model__ and it’s much more computationally intensive. Leis just say that unless you want to wait weeks/months, you’re going to want to perform high accuracy calling on GPUs.
- the __super-accurate__ (SUP or SA) DNA models have higher accuracy than HAC models at the cost of increased compute time. These models take approximately __three times as long__ to run __as a HAC model__, but offer an accuracy improvement over HAC in exchange.

* Added parameters using a RTX3080 16 GB graphic card:

```
sudo systemctl edit guppyd.service --full
```

Edit that service file 

```
ExecStart=/home/myuser/ont-guppy/bin/guppy_basecall_server <things> --chunks_per_runner 160 --chunk_size 2000 -x cuda:all
```
for __SA model__

* Set ```--chunks_per_runner 640``` for __HAC model__ instead of ```--chunks_per_runner 160```.

> The following calculation provides a rough ceiling to the amount of GPU memory that Guppy will use:

memory used [in bytes] = gpu_runners_per_device * chunks_per_runner * chunk_size * model_factor

Where model_factor depends on the basecall model used:
Basecall model 	model_factor
Fast 	1200
__HAC__ 	__3300__
__SUP__ 	__12600__

Note that gpu_runners_per_device is a limit setting. Guppy will create at least one runner per device and will dynamically increase this number as needed up to gpu_runners_per_device. Performance is usually much better with multiple runners, so it is __important to choose parameters such that__ chunks_per_runner * chunk_size * model_factor is __less than half the total GPU memory available__. If this value is more than the available GPU memory, Guppy will exit with an error.

For example, when basecalling using a SUP model and a chunk size of 2000 on a GPU with 8 GB of memory, we have to make sure that the GPU can fit at least one runner:


chunks_per_runner * chunk_size * model_factor should be lower than GPU memory
chunks_per_runner * 2000 * 12600 should be lower than 8 GB
chunks_per_runner lower than ~340

This represents the limit beyond which Guppy will not run at all. For best performance we recommend using an integer fraction of this number, rounded down to an even number, e.g. a third (~112) or a quarter (~84). Especially for fast models, it can be best to have a dozen runners or more. The ideal value varies depending on GPU architecture and available memory.



```
sudo service minkown stop
sudo service guppyd stop
sudo service guppyd start
```

* Confirm the guppy_basecall_server is running and is using the GPU:

``` 
nvidia-smi
``` 

* Start the MinKNOW service:

```
sudo service minknow start
```

# To check all services available and their state
(can help to check if guppyd and minkown service are avilable and enable)

```
sudo systemctl list-unit-files 
```

# Make MinKNOW able to work offline

> This is requested to run MinION sequencing without network (in the field)

In order to change your Linux version of MinKNOW to the offline version, __after usual standard installation__, do the following:
- Install latest version of the software.
- Disable the WiFi to prevent connection after restarting.
- Shutdown the computer/device
- Remove the ethernet cable
- Power on the computer/device
- Open a terminal and run the following commands:

```
sudo /opt/ont/minknow/bin/config_editor --filename /opt/ont/minknow/conf/sys_conf --conf system --set on_acquisition_ping_failure=ignore
```

- Restart the MinKNOW service by running the following commands:

``` 
sudo systemctl daemon-reload
sudo systemctl enable minknow
sudo systemctl start minknow
``` 

- Shutdown the computer/device
- Power on the computer/device


<!-- # fast-bonito -->

<!-- Download of env_gpu.yml from https://github.com/EIHealth-Lab/fast-bonito.git -->

<!-- ``` -->
<!-- # Setup environment using conda -->
<!-- conda env create -f env_gpu.yml  -->
<!-- conda env update -f env_gpu.yml -->
<!-- source activate fast-bonito -->

<!-- # Install fast-bonito -->
<!-- git clone https://github.com/EIHealth-Lab/fast-bonito.git -->
<!-- cd fast-bonito -->
<!-- python setup.py install -->
<!-- ``` -->

<!-- * Error message obtained for first test described [here](https://discuss.pytorch.org/t/received-0-items-of-ancdata-pytorch-0-4-0/19823) (Pytorch problem) -->
<!-- * __solved__ by __adding__ at just before the fast-bonito command in bash script (can be set at the end of __~/.bashrc__):   -->
<!-- ```ulimit -n 4096``` -->


<!-- # bonito -->

<!-- from [github](https://github.com/nanoporetech/bonito) -->

<!-- ``` -->
<!-- sudo apt install pkg-config libhdf5-dev -->
<!-- pip install -f https://download.pytorch.org/whl/torch_stable.html ont-bonito-cuda111 -->
<!-- bonito download --models --latest -f -->
<!-- ``` -->

<!-- > bonito models are also used by fast-bonito -->

