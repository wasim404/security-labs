# 【SQL注入】

## 概念

SQL注入是一种将SQL代码插入或添加到应用（用户）的输入参数中的攻击，之后再将这些参数传递给后台的sql服务器加以解析和执行。

> 当应用程序没有正确验证用户输入或过滤掉危险字符时，就可能发生SQL注入。攻击者可以通过在输入字段中输入特定的SQL语句，这些语句会与后端数据库执行的查询结合，从而改变查询逻辑或执行额外的命令。

## 原理

正常SQL查询代码

`SELECT * FROM users WHERE username = 'user1' AND password = 'password1';`

若攻击者将用户名输入`admin'--`，那么不需要密码就可以登陆，因为此时SQL查询语句为`SELECT * FROM users WHERE username = 'admin' --' AND password = 'anything';`，其中`--`是SQL的注释符号，会忽略密码条件。

## 补充要点

1. `+`会被URL解码为空格，因此要输入`--+`进行注入
2. 表：表是数据库中数据存储的基本单元，它可以被看作是一个由行和列组成的二维结构。
3. 列：列是指表中垂直排列的一组相关数据项。每一列对应一个特定的字段，并包含该字段的所有值。 
4. 字段：字段实际上是指表中的一个列。它代表了表中每个记录的某个属性或特征。可以认为是**列标题**
5. 视图：视图（View） 是数据库管理系统中的一个逻辑表，它并不存储数据本身，而是**基于SQL查询的结果集**。视图可以包含来自一个或多个表的数据，并且可以根据需要对这些数据进行筛选、聚合等操作。可以认为是查询结果拼凑成的一张表
6. **`information_schema`**：这是符合 SQL 标准的元数据库，存储了关于数据库元数据的信息。其中`schemata`表包含了所有数据库（在MySQL术语中称为schemas）的相关信息。而`schema_name` 是 `information_schema.schemata` 这张表中的一个字段（列），专门用于存放每个数据库的名称。
7. **`group_concat()`**：这是一个聚合函数，用来将多行结果合并成一行，并以指定的分隔符连接起来。默认情况下，它使用逗号作为分隔符。
8. 连接phpstudyMySQL数据库指令：`mysql -u root -p`
9. **GET / POST / COOKIE / REQUEST** 等所有用户输入的值，在 PHP 里最初都是字符串类型。也就是说，在php里，即使你输入`?id=1`，会被认为是`'1'`
10. `isset($a, $b, $c)` **只有在所有列出的变量都已定义且都不是 `null` 时才返回 `true`**。任意一个变量不存在或是 `null`，整个 `isset(...)` 就返回 `false`。

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

`users`表 的 `id` 字段定义为 `INT`（整数），而传入的id是一个字符串，MYSQL会从字符串最左边开始读，只要遇到连续的数字（可带正负号、小数点），就取这部分；一旦遇到非数字字符，就停止，后面全部忽略，然后进行比较。

注意：**必须要准确判断出闭合方式才能进行下一步操作，否则无法使用order by正确判断回显位**

## 注入类型检测

### 字符型注入

后端 SQL 语句中，用户输入**被单引号（或双引号）包裹。**

检测：输入`?id=1'`报错，说明是字符型

### 数字型注入

后端 SQL 语句中，用户输入**不被单引号（或双引号）包裹。**

检测：输入`?id=1 and 1=1`正常，但是`?id=1 and 1=2`错误

### 搜索型注入

在网站的搜索框中可能存在搜索型注入

在 SQL 的 `LIKE` 模糊匹配中，**`%` 和 `_` 是两个非常重要的通配符**

`%`含义：匹配 **任意长度的任意字符（包括零个字符）**，相当于正则表达式中的`*`

`_`含义：匹配 **恰好一个任意字符**

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

## 联合查询注入

联合注入（Union-based SQL Injection）是一种SQL注入技术，它利用了SQL中的`UNION`操作符来合并两个或多个`SELECT`语句的结果集。攻击者通过这种方法可以从数据库中提取额外的信息，如表名、列名以及其中的数据。

步骤：

1. 判断注入点（也就是如何闭合）

2. 爆回显列数，输入`order by 3--+`，逐步增加，直到不正常回显。

3. 强制前一个查询不返回任何行，这样可以让`UNION SELECT`部分的结果成为整个查询的唯一输出。方法有`?id=1' and 1=2 union select...`或者是`id = -1' union select...`

4. 爆出所有数据库名称`union select 1,2,group_concat(schema_name) from information_schema.schemata--+`

   > `group_concat(schema_name)`的作用是从`information_schema.schemata`表中选择所有的`schema_name`字段值，并将这些值通过逗号或其他指定的分隔符连接起来作为一个单一的结果返回。这使得你能够一次性查看**所有数据库的名字**

5. 爆出关键数据库下所有的表的名称` union select 1,2,group_concat(table_name) from information_schema.tables where table_schema='ctfshow'--+`

   > `information_schema.tables`就是所有表的名单，`table_schema`就是在哪个数据库，`table_name`就是表的名称

## 报错注入

## 布尔型注入

## 时间延迟注入

## 多语句查询注入

