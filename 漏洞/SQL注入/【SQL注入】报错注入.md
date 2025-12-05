# 【SQL注入】报错注入

## 简介

报错注入（Error-based Injection）是SQL注入攻击中的一种常见技术，它利用数据库在**执行异常SQL语句时返回的错误信息**，从中提取敏感数据或推断数据库结构。

## 方法

常见的报错注入有以下手法

### Updatexml()函数

```
updatexml(XML_document, XPath_string, new_value)
```

- **参数1 (`XML_document`)**：XML文档对象名称（字符串格式）。
- **参数2 (`XPath_string`)**：XPath格式的字符串（路径）。这是关键点，该参数必须符合XPath语法规范（例如 `/xxx/xxx`）。
- **参数3 (`new_value`)**：要更新的新值（字符串格式）。

如果我们在**第二个参数**的位置填入**不符合XPath语法的字符串（例如以数字或特殊符号开头）**，MySQL就会执行报错，并且**报错信息中会包含我们填入的非法内容**。我们正是利用这一点，把我们想要查询的SQL语句（如 `database()`）嵌套进去，让数据库“被迫”把数据展示在报错里。

常见核心构造公式

`and updatexml(1, concat(0x7e, 查询语句, 0x7e), 1) --+`

> 0x7e解码后就是~，0x23解码后就是#

#### 优化

使用`substring`截取返回字符串，这是由于`updatexml`报错的局限性，因为`updatexml` 报错最多只显示 **32 个字符**，当返回的信息较多时，就必须要进行截取。

例如`and updatexml(1, substring(concat(0x7e,(select group_concat(schema_name) from information_schema.schemata),0x7e), 1, 32), 1) --+`这样就是返回第1-32个字符

`and updatexml(1, substring(concat(0x7e,(select group_concat(schema_name) from information_schema.schemata),0x7e), 33, 64), 1) --+`这样就是返回第33-64个字符

## 步骤

报错注入适用于页面有回显错误信息

1. 判断闭合方式（注入类型）
2. 判断回显位
3. 使用对应报错注入方法

