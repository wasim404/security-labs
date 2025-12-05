# 【SQL注入】注入类型

## 字符型注入

后端 SQL 语句中，用户输入**被单引号，双引号这些字符包裹。**

可能是`$sql = "SELECT * FROM users WHERE username = '$username'";`

构造payload后执行实际的语句可能为`SELECT * FROM users WHERE username = 'admin' --'`

检测：输入`?id=1'`报错，说明是字符型

## 数字型注入

后端 SQL 语句中，用户输入**不被单引号（或双引号）包裹。**

`$sql = "SELECT * FROM articles WHERE id = $id"`

构造payload后执行实际的语句可能为`SELECT * FROM articles WHERE id = 1 OR 1=1`

检测：输入`?id=1 and 1=1`正常，但是`?id=1 and 1=2`错误

## 搜索型注入

在网站的搜索框中可能存在搜索型注入

在 SQL 的 `LIKE` 模糊匹配中，**`%` 和 `_` 是两个非常重要的通配符**

`%`含义：匹配 **任意长度的任意字符（包括零个字符）**，相当于正则表达式中的`*`

`_`含义：匹配 **恰好一个任意字符**

构造payload后执行实际的语句可能为`SELECT * FROM products WHERE name LIKE '%\' OR \'1\'=\'1\' --%'`