# 【渗透测试】vulhub靶场使用

这里使用Ubuntu，方便靶场搭建

## Ubuntu虚拟机搭建

UbuntuISO文件下载地址：`[Download Ubuntu Desktop | Ubuntu](https://ubuntu.com/download/desktop)`

或者这里是我下载好的ISO文件： https://pan.baidu.com/s/1HTxa1zy4_J2SoNcBHgKEhw?pwd=flag 提取码: flag 


关于vmware下载和虚拟机配置请自行查找资料（这部分很简单）

建议在输入指令前，先输入`sudo su`来提升权限，这样以后输入指令可以省去`sudo`。

## vmware tools下载安装

下载这个，便于我们复制粘贴复杂指令

1. 在Ubuntu的终端中依次输入以下内容，就安装好了

```bash
sudo apt update
sudo apt install -y open-vm-tools open-vm-tools-desktop
sudo reboot
```

2. 在Ubuntu终端中复制内容为`ctrl+shift+C`，粘贴内容为`ctrl+shift+V`

## 安装pip

> 倘若以下给出的指令无效了，或是遇到任何意料之外的问题，首先我们可以尝试系统给我们推荐的指令（通常会在报错信息的末尾部分），然后可以问问其他佬，看看视频，询问AI。

通常来说，Ubuntu默认自带python3，输入`python3 -v`，若能输出python3版本，则说明系统已经安装好了

输入以下指令安装pip

```bash
sudo apt install -y python3-pip
```

输入`pip -V`，若能返回pip版本信息，说明安装成功

## 安装docker

输入以下指令安装docker

```bash
sudo apt install docker.io
```

输入`docker`，若返回相关信息，说明安装成功

## 安装compose

```bash
sudo apt install docker-compose
```

输入`docker-compose`，若返回相关信息，说明安装成功

## git克隆文件

1. 确认好你电脑上科学上网（比如说clash）的监听端口，一般在首页能找到，假设说是7890

2. 在Windows的终端中，输入`ipconfig`获取虚拟机IP，会看到`以太网适配器 VMware Network Adapter VMnet1`这种字样

3. 在Ubuntu终端中依次输入以下指令，其中`xx`部分是你的虚拟机IP，若不确定哪个是Ubuntu的，那就都去尝试一下，哪个能用就是哪个。`yy`是你第一步确认的监听端口

   ```bash
   git config --global http.proxy http://xx:yy
   git config --global http.proxy https://xx:yy
   git clone https://github.com/vulhub/vulhub.git
   ```

4. 安装好以后，输入`cd vulhub/`进入文件夹，再输入`ls`就可以查看到漏洞文件

## docker代理设置

1. 输入以下指令，创建 systemd 配置目录：

```bash
sudo mkdir -p /etc/systemd/system/docker.service.d
```

2. 一次性复制粘贴以下所有内容到Ubuntu终端，其中xx:yy含义同上文，用于创建代理配置文件：

```bash
sudo tee /etc/systemd/system/docker.service.d/http-proxy.conf <<-'EOF'
[Service]
Environment="HTTP_PROXY=http://xx:yy/"
Environment="HTTPS_PROXY=http://xx:yy/"
Environment="NO_PROXY=localhost,127.0.0.1"
EOF
```

3. 重启docker，读取新配置

   ```bash
   sudo systemctl daemon-reexec
   sudo systemctl restart docker
   ```

输入`sudo docker info | grep -i proxy`，若返回代理的相关信息，说明配置无误

## 启动靶场

1. 进入某一个漏洞的文件夹内部，例如`cd vulhub/spring/CVE-2022-22947`
2. 输入`sudo docker-compose up -d`就能启动靶场

## 访问靶场

1. 输入`docker ps`，可以查看端口映射信息
2. 在虚拟机内部浏览器访问，地址是`http://127.0.0.1:8080`
3. 在宿主机外部浏览器访问，则需要先在Ubuntu终端中，输入`ifconfig`，查看`ens33`的IP地址，完整地址就是`http://xx(ens33的IP地址):8080`







