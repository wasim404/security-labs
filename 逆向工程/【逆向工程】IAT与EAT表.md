# 【逆向工程】导入表与导出表

## DLL

DLL（Dynamic Link Library），动态链接库。

在16位DOS时期，编译器是直接从库(Library)中读取程序中相应函数的二进制代码，然后插入到应用程序中。但现代Windows系统使用大量的库函数，若仍采用这种方式，就会导致效率低下。因此，Windows操作系统引入了DLL的概念

### 作用

1. 程序本身不需要包含这些函数的代码，只需引用 DLL。
2. 多个进程共享同一套函数，不用每个进程都重复实现。
3. 只更新 DLL 文件，就能让所有使用它的程序获得新功能或修复。

### 加载方式

#### 隐式加载（Implicit Linking）

特点：

- 编译阶段就确定需要哪些 DLL。
- EXE 的导入表中写着 DLL 名和函数名。
- **程序启动时由系统 Loader 自动加载 DLL**。

> 程序运行一开始，DLL 就已经在进程里了。如果 DLL 缺失，程序直接启动失败。

#### 显式加载（Explicit Linking）

特点：

- 程序自己在运行时手动加载 DLL。
- 使用 API：
  - `LoadLibrary()`
  - `GetProcAddress()`
- 什么时候加载、加载什么 DLL **完全由程序控制**。

> DLL 可以按需加载、延迟加载。可用于隐藏导入、防静态分析（比如恶意软件常用）。

### 加载地址

EXE文件能准确加载到自身的ImageBase中，是因为每个进程的虚拟地址空间相互隔离，彼此独立。在进程 A 中可以把它映射到 `0x00400000`在进程 B 中也可以把它映射到 `0x00400000`。

> 每个进程都有独立的页表，不同程序的页表不同，最终映射到实际的物理地址也不同，因此不会互相干扰。CPU 中有一个寄存器（CR3）专门保存 **当前进程的页表位置**。

但是DLL会被重复多次加载，有的进程的某个地址（假设是DLL 的默认 ImageBase）可能已经被其他模块占用。这个时候DLL只能重定位到别的位置。因此无法保证加载到指定的 ImageBase，只能根据情况重定位。

## PE装载器

PE 装载器（PE Loader）就是负责把 PE 文件（EXE/DLL）**从磁盘加载到内存**，并让它准备好运行的系统组件。

它主要做的事包括：

- 映射 PE 文件到进程地址空间
- 解析并加载需要的 DLL
- 修复重定位（Relocation）
- 填写 IAT（导入地址表）
- 调用程序的入口点（Entry Point）开始执行

## 导入表（Import Table）

这是导入表的每一项的结构

```c
typedef struct _IMAGE_IMPORT_DESCRIPTOR {
    DWORD   OriginalFirstThunk;   // 指向 INT（导入名称表）
    DWORD   TimeDateStamp;
    DWORD   ForwarderChain;
    DWORD   Name;                 // 指向 DLL 名字（字符串）
    DWORD   FirstThunk;           // 指向 IAT（导入地址表）
} IMAGE_IMPORT_DESCRIPTOR;

```

`OriginalFirstThunk`：指向 **Import Name Table（导入名称表，INT）**的RVA，里面存着“要导入的函数名字/序号”。Loader 用它来解析函数真实地址。

`Name`：DLL 的名字，例如`"KERNEL32.dll"`，也是RVA

> 程序导入多少 DLL，就需要多少个导入描述符。

`FirstThunk`：指向 **导入地址表**的RVA，Loader 会把解析出的真实 API 地址写入这里，程序运行时真正 `call` 的就是这个表里的地址。

> 导入描述符的地址：在PE头中的可选头的`DataDirectory[1]`

### 各类表信息查看

> 接下来讲一下如何查看程序中的表的信息

首先，通常情况下，PE头结构中的可选头的倒数128字节开始至结束，就是`IMAGE_DATA_DIRECTORY DataDirectory[IMAGE_NUMBEROF_DIRECTORY_ENTRIES]`部分，这里面储存了程序运行相关的表的信息。每8个字节代表一个表，其中前4个字节是表RVA，后4个字节是表的大小。

> 在010editor中，鼠标悬停在对应位置时，会显示出该位置的结构体信息。

![](C:\Users\34743\Desktop\表信息.png)

上面这张图片就是`IMAGE_DATA_DIRECTORY DataDirectory[IMAGE_NUMBEROF_DIRECTORY_ENTRIES]`部分，当鼠标悬停在比如说`78 65 54 00`部分就会显示如下提示

![](C:\Users\34743\Desktop\导入表展示.png)

这说明了导入表的RVA是`0x00546578`（小端序）。

第二步，就是将RVA转换成在磁盘中的地址

这需要确定导入表在哪个节里，因此，要看节区头信息

![](C:\Users\34743\Desktop\节区头.png)

按照结构体定义，节区名称占8个字节，节区在内存中的大小占4字节，后面的4个字节就是节区的RVA。

![](C:\Users\34743\Desktop\节区RVA.png)

上面的图片就可以分析出，text节区在内存中从`0x00001000`开始，占`0x0044D808`大小，并且还要按照`SectionAlignment` 设置的大小对齐。

由此一步步就可分析出导入表在`.rdata`节中。`.rdata`节的`VirtualAddress`是`0x0044F000`，`PointerToRawData`是`0x0044DE00`。

根据公式

`RAW = (RVA - Section[i].VirtualAddress) + Section[i].PointerToRawData`

就可以算出导入表在磁盘中地址是`0x545378`

例如，这就是导入表其中的一个元素

![](C:\Users\34743\Desktop\导入表.png)

### 导入表查看

现在我们根据上面的方法，查看导入表内容。

按照上图的例子`3C 7B 54 00`，也就是RVA为`0x00547B3C`的地方应该存放一个DLL名称信息，按照公式转化，对应文件偏移地址就是`0x54693C`

![](C:\Users\34743\Desktop\dll名称.png)

RVA为`0x005467B0`指向INT表，RVA为`0x0044F0A8`指向对应的IAT表。

## INT表

INT表记录了该程序调用对应的DLL文件中的函数名称或序号。

PE文件中，每个元素4个字节

PE+文件中，每个元素8个字节

**当INT表中元素代表函数名称时**

结构特征是**最高位为0**，（注意小端序），所以在010editor中查看就会类似于`0C 7B 54 00 00 00 00 00`，这是一个RVA，也就是`0x0000000000547B0C`。但是这个RVA指向的是IMAGE_IMPORT_BY_NAME（一个“函数结构”），不是函数名。

**当INT表中元素代表函数在DLL中序号时**

结构特征是**最高位为1**，在010editor中查看类似于`7D 01 00 00 00 00 00 80`，（因为`0x80 00`按照二进制展开就是`1000 0000`）。对于PE文件，序号占 **低 31 位**；对于PE+文件，序号占 **低 63 位**。（也就是去掉1后剩下的内容）

> 例如，PE文件中若是0x80000054，二进制展开就是`1000 0000 0000 0000 0000 0000 0101 0100`，那么序号部分就是`000 0000 0000 0000 0000 0000 0101 0100`，也就是`0x54`。

### 查看INT表元素

按照上文例子，将`0x0000000000547B0C`这个RVA转化后是`0x5488A0`，跳转查看。

![](C:\Users\34743\Desktop\INT元素.png)

当INT元素代表函数名称时，指向的IMAGE_IMPORT_BY_NAME结构是

```c
typedef struct _IMAGE_IMPORT_BY_NAME {
    WORD Hint;
    CHAR Name[1];    // 以 '\0' 结尾的 ASCII 函数名
} IMAGE_IMPORT_BY_NAME;

```

其中，前两个字节只是为了优化搜索的提示值，不重要。后面紧跟着就是真正的函数名了。

当INT元素代表函数在DLL中序号时，

> 有点复杂

## IAT表

作用：程序真正使用的函数地址都在 IAT 里面。程序运行中访问 API 时，访问的是 IAT，而不是 INT。

当文件未加载运行时，IAT和INT内容**完全一样**。

也就是说：

- 如果按名称导入 → IAT[i] 是指向 IMAGE_IMPORT_BY_NAME 的 RVA
- 如果按序号导入 → IAT[i] 也存一个数值（最高位=1）

当 Windows 加载进程时，Loader 做三件事：

1. 根据 INT 找到所有函数的名字（或序号）
2. 在 DLL 的导出表中查到它们真实的函数地址
3. **把真实函数地址写入 IAT 中**

> 举个例子，IAT在程序加载前比如说保存了CreateFileA，当程序加载时，就会被loader替换为0x76F01234（真实函数地址）

## 导出表（Export Table）

作用：记录一个 DLL **对外提供**的所有函数/变量的列表。

> 导出表是一个结构体IMAGE_EXPORT_DIRECTORY
>
> 一个PE文件只有一个导出表

```c
typedef struct _IMAGE_EXPORT_DIRECTORY {
    DWORD   Characteristics;        // 一般为 0
    DWORD   TimeDateStamp;		  
    WORD    MajorVersion;		   // 一般为 0
    WORD    MinorVersion;		   // 一般为 0
    DWORD   Name;                   // DLL 名称（RVA）
    DWORD   Base;                   // 导出函数序号的起始值
    DWORD   NumberOfFunctions;      // 导出函数数量（可能包含空）
    DWORD   NumberOfNames;          // 有名称的导出函数数量
    DWORD   AddressOfFunctions;     // 导出函数地址表 RVA (EAT)
    DWORD   AddressOfNames;         // 导出函数名称表 RVA
    DWORD   AddressOfNameOrdinals;  // 导出函数序号表 RVA
} IMAGE_EXPORT_DIRECTORY, *PIMAGE_EXPORT_DIRECTORY;
//共40个字节
```

### 查看导出表信息

> 下面是在 EAT中查找指定函数的步骤教程

#### 以函数名称查找信息

1. 回到可选头部分，查看导出表的RVA是`0x546470`，转换后就是`0x545270`，跳转到`0x545270`

   ![](C:\Users\34743\Desktop\导出表.png)

2. 找到`AddressOfNames`的RVA是`0x005464B8`，转换后是`0x5452B8`

   `AddressOfNames`的内容是指向各个函数名字符串的RVA（每4个字节为一个RVA）

   ![](C:\Users\34743\Desktop\函数RVA.png)

   也就是说RVA为`0x005464F6`就对应一个函数名，其索引值为0。转换后就是`0x5452F6`

   ![](C:\Users\34743\Desktop\函数名.png)

   这就是一个叫做`CreateLexer`的函数

3. 找到`AddressOfNameOrdinals`的RVA是`0x005464D8`，转换后是`0x5452D8`，然后**这个表对应的索引值的值当作新的序号**。

   > 也就是说，函数在`AddressOfNames`里的索引值假设为i (下标从0开始)，那么新的序号就是`AddressOfNameOrdinals[i]`
>
   > 注意，这个表是两个字节为一个元素
   
   
   
   ![](C:\Users\34743\Desktop\AOO.png)
   
   观察表发现，索引为0的地方对应的值也是0
   
4. 找到`AddressOfFunctions`的RVA是`0x546498`，转换后就是`0x545298`

   ![](C:\Users\34743\Desktop\aof.png)

   得到`CreateLexer`的函数的RVA是`0x2EF0F0`，转换后就是`0x2EE4F0`，就可以看到函数实现了

> 总结一下流程：导出表--->AddressOfNames看函数名+记住索引--->AddressOfNameOrdinals看上一步索引值对应元素的值(2个字节)，作为新的序号--->AddressOfFunctions看新的序号位置对应的值（4字节）就是函数的RVA

#### 以函数序号查找信息

> 函数在DLL中的序号：将`AddressOfNameOrdinals`表中的值加上Base

1. 将函数序号减去Base（查看导出表的Base），得到一个索引
2. 将这个索引作为`AddressOfFunctions`表中的索引，就可以得到想要的函数的RVA