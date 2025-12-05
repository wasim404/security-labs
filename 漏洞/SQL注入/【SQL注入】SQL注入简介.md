# 【SQL注入】SQL注入简介

## 概念

SQL注入是一种将**SQL代码插入或添加到应用（用户）的输入参数**中的攻击，之后再将这些参数传递给后台的sql服务器加以解析和执行。

> 当应用程序没有正确验证用户输入或过滤掉危险字符时，就可能发生SQL注入。攻击者可以通过在输入字段中输入特定的SQL语句，这些语句会与后端数据库执行的查询结合，从而改变查询逻辑或执行额外的命令。

## 原理

正常SQL查询代码

`SELECT * FROM users WHERE username = 'user1' AND password = 'password1';`

若攻击者将用户名输入`admin'--`，那么不需要密码就可以登陆，因为此时SQL查询语句为`SELECT * FROM users WHERE username = 'admin' --' AND password = 'anything';`，其中`--`是SQL的注释符号，会忽略密码条件。

## MYSQL注入的文件读写操作

MySQL的安全变量`secure_file_priv`限制了可以读取/写入的文件目录

`SHOW VARIABLES LIKE 'secure_file_priv';`

- 如果返回值是 `NULL`：**禁止**所有文件读写。
- 如果返回值是某个路径（如 `C:\ProgramData\MySQL\MySQL Server 8.0\Uploads\`）：只能读该目录下的文件。
- 如果返回值是空字符串 `''`：表示不限制（但 MySQL 8.0+ 默认不为空）。

修改权限：修改phpstudy的root用户的权限为可读写文件，在`my.ini`的文件中的[mysqld]下添加`secure_file_priv =`即可。

文件读写操作调用的函数因数据库而异

MySQL数据库中使用

- `load_file()`：读取文件函数
- `into outfile 或into dumpfile`：文件写入函数,`INTO OUTFILE` 只能创建新文件，不能覆盖已有文件。

示例

```mysql
mysql> select load_file('d:/test.txt');
+--------------------------+
| load_file('d:/test.txt') |
+--------------------------+
| 1111                     |
+--------------------------+
1 row in set (0.00 sec)
```

网站路径获取方法

1. 报错显示
2. 遗留文件
3. 漏洞报错
4. 平台配置文件

### 魔术引号

PHP 中主要有三种魔术引号配置（通过 `php.ini` 设置）：

1. **magic_quotes_gpc**
   - 影响：`$_GET`、`$_POST`、`$_COOKIE`
   - 默认在 PHP 5.3.0 之前是开启的（值为 `On`）。
2. **magic_quotes_runtime**
   - 影响：从外部资源（如数据库、文件）读取的数据
   - 会自动对运行时获取的数据进行转义。
3. **magic_quotes_sybase**
   - 如果启用，会改变转义方式：使用两个单引号 `''` 而不是反斜杠来转义单引号（模仿 Sybase 数据库的行为）。

![image-20251021162746343](C:\Users\34743\AppData\Roaming\Typora\typora-user-images\image-20251021162746343.png)

绕过魔术引号的方式：

**将文件路径进行hex十六进制编码**

## MYSQL类型转换

在`SQLi Labs`靶场中，有时候发现即使闭合方式是`')`，但是构造`?id=1"`仍可以成功查询得到`id=1`的账号，是因为MYSQL存在**隐式类型转换**，也就是**MySQL 会自动把字符串转换成数字，然后再进行比较。**

`users`表 的 `id` 字段定义为 `INT`（整数），而传入的id是一个字符串，MYSQL会从字符串最左边开始读，只要遇到连续的数字（可带正负号、小数点），就取这部分；一旦遇到非数字字符，   停止，后面全部忽略，然后进行比较。

注意：**必须要准确判断出闭合方式才能进行下一步操作，否则无法使用order by正确判断回显位**

## 注入防护

1. 参数化查询：SQL语句的结构和数据（用户输入）分开处理，**参数化查询**不是把输入拼进去，而是这样做（伪代码）：

   ```mysql
   -- 发送给 DB 的语句（含占位符）
   SELECT * FROM users WHERE id = :id LIMIT 0,1
   
   -- 参数（单独发送）
   :id => "1'--+"
   ```

   数据库会把 `:id` 绑定的值当**纯数据**处理（作为一个字符串或整数值），不会当 SQL 片段解析。所以即便参数是 `1'--+`，它也只是一个值，查询就变成查找id有无等于`1'--+`而不会被绕过

2. 输入白名单：仅允许用户输入白名单中的内容，其余一并报错

## 

