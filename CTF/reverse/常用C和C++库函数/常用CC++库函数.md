# 常用C/C++库函数

## 字符串相关函数

| 函数名     | 原型                                                         | 作用                                                     | 返回值                                                       |
| ---------- | ------------------------------------------------------------ | -------------------------------------------------------- | ------------------------------------------------------------ |
| `strstr`   | `char *strstr(const char *haystack, const char *needle);`    | 在字符串 `haystack` 中查找子串 `needle` 的第一次出现位置 | 找到则返回指向子串开头的指针；找不到返回 `NULL`              |
| `strcmp`   | `int strcmp(const char *s1, const char *s2);`                | 比较两个字符串的字典序                                   | 返回值有三种情况， `<0` / `0` / `>0`，分别对应表示 `s1 < s2` / 相等 / `s1 > s2` |
| `strcpy`   | `char *strcpy(char *dest, const char *src);`                 | 把 `src` 字符串（含结尾 `\0`）复制到 `dest`              | 返回 `dest`                                                  |
| `strcpy_s` | `errno_t strcpy_s(char *dest, rsize_t destsz, const char *src);` | 安全版本复制字符串，要求提供目标缓冲区大小               | 成功返回 `0`，失败返回非 0 错误码（并会将目标清零）          |
| `strncmp`  | `int strncmp(const char *s1, const char *s2, size_t n);`     | 比较前 `n` 个字符                                        | 同 `strcmp`                                                  |
| `strncpy`  | `char *strncpy(char *dest, const char *src, size_t n);`      | 最多复制 `n` 个字符到 `dest`                             | 返回 `dest`                                                  |

## 内存操作相关函数

| 函数名   | 原型                                      | 作用                                             | 返回值   |
| -------- | ----------------------------------------- | ------------------------------------------------ | -------- |
| `memset` | `void *memset(void *s, int c, size_t n);` | 将连续的 n 个字节都设置为“值为 c 的最低 8 bit”。 | 返回 `s` |
|          |                                           |                                                  |          |
|          |                                           |                                                  |          |

注意点：

`memset`是按字节填充，不是按照整数填充。

```c
char a[4];
memset(a, 12, 4); // 没问题，因为一个元素只占用一个字节。

int a[4];
memset(a, 12, sizeof(a));// 错误，因为此时数组中一个元素占四个字节，程序会把一个int（4字节）中的每一个字节都填充为0x0C(十六进制的12)，最终每个元素变为0x0C0C0C0C

```



