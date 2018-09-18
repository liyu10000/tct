
## 通用算法环境部署

## 一 系统安装

### 1.1 分区

适用于 512g nvme 和 1个机械硬盘的情况

    /boot 20g nvme
    /     剩下的nvme
    /swap 200g nvme
    /home 机械硬盘

### 1.2 基础服务和包 

准备安装环境：

    可视化切换源到aliyun
    sudo apt update
    sudo apt upgrade
    sudo install vim

安装ssh：

    sudo apt install openssh-server

samba:
    
    sudo apt install samba
    sudo apt install smbclient
    
    sudo vi /etc/samba/smb.conf
        
        用户名:sakulaki
        共享目录:/home/sakulaki
    
        在最后添加
        [sakulaki]
        comment = Share Folder require password
        browseable = yes
        path = /home/sakulaki
        create mask = 0777
        directory mask = 0777
        valid users = sakulaki
        force user = nobody
        force group = nogroup
        public = yes
        writable = yes
        available = yes
        
    sudo /etc/init.d/samba restart
    cd /home
    sudo mkdir sakulaki
    chmod 777 sakulaki
    sudo groupadd sakulaki -g 6000
    sudo useradd sakulaki -g 6000 -s /shin/nologin -d /dev/null
    
    sudo smbpasswd -a sakulaki
    输入两次密码即可（建议123）

ip设置:
    
    在图形界面中设置相关ip
    ipv4选项卡，设置地址
    IP地址：192.168.1.xx
    mask: 255.255.255.0
    网关：192.168.1.1
    dns: 192.168.1.1

后续准备：
    
    samba 192.168.1.123/sakulaki 的env文件夹
    从该文件夹复制所有的env 到 需要安装的机器 samba 的env
    
    解压env下的archives 到指定机器的 /var/cache/apt/archives 中

## 二 系统基础库安装

## 2.1 ubuntu base 

编译环境

    sudo apt install build-essential ssh git cmake dkms

### 2.1 NVIDIA相关

驱动：
    
    sudo add-apt-repository ppa:graphics-drivers/ppa
    sudo apt update
    sudo apt install nvidia-396
    sudo reboot

CUDA:
    
    cd /home/sakulaki/env
    sudo chmod +x cuda_9.0.176_384.81_linux.run
    sudo ./cuda_9.0.176_384.81_linux.run
    
    Accept EULA
    Say No to installing the NVIDIA driver
    Say Yes to installing CUDA Toolkit
    Say No to installing CUDA Samples
    vim ~/.bashrc
    add:
    export PATH=/usr/local/cuda_9.0/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda_9.0/lib64:$LD_LIBRARY_PATH
    source ~/.bashrc
    nvcc -V
    
    
    
    

CUDNN:

    sudo dpkg -i libcudnn7_7.1.4.18-1+cuda9.0_amd64.deb
    sudo dpkg -i libcudnn7-dev_7.1.4.18-1+cuda9.0_amd64.deb

install tslide

    sudo unzip tslide.zip
    cd tslide
    sudo cp -r *.so /usr/lib

### 三 虚拟环境安装 

anaconda安装

    sudo chmod +x Anaconda3-5.2.0-Linux-x86_64.sh
    sudo ./Anaconda3-5.2.0-Linux-x86_64.sh
    记得添加环境变量 yes

anaconda环境创建
    
    tar -xvf keras-base.tar
    conda create -n algo-base --clone ~/../sakulaki/env/algo-base
    conda create -n algo-work --clone algo-base

jupyter remote setting

    jupyter notebook --generate-config
    
    In [1]: from notebook.auth import passwd
    In [2]: passwd()
    Enter password: 123
    Verify password: 123
    Out[2]: 'sha1:f2aad3cde3ea:e3b48d4cd230beeb3e6753617f38aaf77fc785cd'
    把密文复制下来 'sha1:f2aad3cde3ea:e3b48d4cd230beeb3e6753617f38aaf77fc785cd'
    
    vim ~/.jupyter/jupyter_notebook_config.py 
    c.NotebookApp.ip='*'
    c.NotebookApp.password = u'sha1:f2aad3cde3ea:e3b48d4cd230beeb3e6753617f38aaf77fc785cd'
    c.NotebookApp.open_browser = False
    c.NotebookApp.port = 8888

anaconda环境激活和使用
    
    source activate algo-work
    在想使用的文件夹下 jupyter notebook
    在局域网内任意机器输入 192.168.1.xx:8888 即可访问

### 四 未尽事宜

    使用super机作为安装镜像服务器
    
    使用本地deb作为apt安装源


```python

```
