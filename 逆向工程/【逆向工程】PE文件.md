# 【逆向工程】PE文件

## COFF

COFF（**Common Object File Format**）是一种通用目标文件格式，用于存储编译器生成的机器代码、符号表、重定位信息等，是早期 UNIX 和 Windows 系统目标文件与可执行文件的基础格式。Windows 的 **PE（Portable Executable）** 格式实际上是 COFF 的扩展；ELF 则是其后继改进。

> COFF 是**目标文件标准格式**，连接编译器与链接器，是现代 **PE** 与 **ELF** 的祖先格式。

## PE文件

PE文件是32位可执行文件，也称为PE32

PE+是64位可执行文件，也称为PE32+

### PE文件种类

| 类别             | 文件类型                          | 常见扩展名 | 主要用途                 | 是否可独立执行   |
| ---------------- | --------------------------------- | ---------- | ------------------------ | ---------------- |
| **可执行系列**   | Executable Image（可执行文件）    | `.exe`     | 普通用户态程序           | ✅ 是             |
|                  | Console Application（控制台程序） | `.exe`     | 命令行程序               | ✅ 是             |
|                  | GUI Application（图形程序）       | `.exe`     | 图形界面应用             | ✅ 是             |
|                  | Screen Saver（屏幕保护程序）      | `.scr`     | Windows 屏保（实为 EXE） | ⚠️ 否（系统调用） |
| **驱动程序系列** | Kernel Driver（内核驱动）         | `.sys`     | 内核态驱动程序           | ⚠️ 否             |
|                  | Legacy Driver / Virtual Device    | `.drv`     | 旧式驱动、设备控制模块   | ⚠️ 否             |
| **库系列**       | Dynamic-Link Library（动态库）    | `.dll`     | 动态链接库函数           | ⚠️ 否             |
|                  | Control Panel Applet              | `.cpl`     | 控制面板插件             | ⚠️ 否             |
|                  | ActiveX / COM Component           | `.ocx`     | 可复用组件库             | ⚠️ 否             |
| **对象文件系列** | Object File（目标文件）           | `.obj`     | 编译中间产物             | ⚠️ 否             |
|                  | Import Library（导入库）          | `.lib`     | 链接 DLL 的符号表        | ⚠️ 否             |
|                  | Static Library（静态库）          | `.lib`     | 链接时合并进可执行文件   | ⚠️ 否             |

## PE文件结构

### DOS头

**DOS 头（IMAGE_DOS_HEADER）** 是 PE 文件最开始的结构，用来兼容早期的 DOS 系统，并提供一个指针 (`e_lfanew`) 指向真正的 PE 头，共 64 个字节。

DOS头结构体原型

```c
typedef struct _IMAGE_DOS_HEADER {
    WORD   e_magic;    // 魔数："MZ"
    WORD   e_cblp;
    WORD   e_cp;
    WORD   e_crlc;
    WORD   e_cparhdr;
    WORD   e_minalloc;
    WORD   e_maxalloc;
    WORD   e_ss;
    WORD   e_sp;
    WORD   e_csum;
    WORD   e_ip;
    WORD   e_cs;
    WORD   e_lfarlc;
    WORD   e_ovno;
    WORD   e_res[4];
    WORD   e_oemid;
    WORD   e_oeminfo;
    WORD   e_res2[10];
    LONG   e_lfanew;   // 指向 PE 头的文件偏移
} IMAGE_DOS_HEADER, *PIMAGE_DOS_HEADER;
```

重要成员

1. `e_magic`，固定值为`0x4D5A`（ASCII 对应 `"MZ"`），作用是标识该文件为 DOS 可执行文件（“Mark Zbikowski” 的首字母，微软工程师名）。加载器读取前两个字节若不是 `"MZ"`，则判定该文件不是有效可执行文件。
2. ` `，存放 **PE Header** 在文件中的偏移地址。如果 `e_lfanew = 0x00000100` ，则PE 签名 `"50 45 00 00"` 从文件偏移 `0x100` 开始。

![](C:\Users\34743\Desktop\DOS头.png)

上述示例说明PE头位置是`0x00000128`

### DOS存根

DOS 存根（DOS Stub）是紧跟在 64 字节 DOS 头之后的一段 16 位 DOS 可执行代码。当在 DOS 环境下运行 PE 文件时，DOS 会执行这段代码，通常用于显示 “This program cannot be run in DOS mode.” 并安全退出。

DOS 存根的大小不固定，但 Microsoft 链接器生成的标准存根为 64 字节，因此 DOS 头（64 字节）加上存根（64 字节）总共为 128 字节

即使没有DOS存根，文件也能正常运行。

![](C:\Users\34743\Desktop\DOS存根.png)

### NT头

```c
typedef struct _IMAGE_NT_HEADERS {
    DWORD Signature;                 // "PE\0\0" 签名
    IMAGE_FILE_HEADER FileHeader;    // 文件头
    IMAGE_OPTIONAL_HEADER OptionalHeader; // 可选头
} IMAGE_NT_HEADERS, *PIMAGE_NT_HEADERS;
```

#### 文件头

```c
typedef struct _IMAGE_FILE_HEADER {
    WORD  Machine;              // 目标机器类型
    WORD  NumberOfSections;     // 节（Section）数量
    DWORD TimeDateStamp;        // 时间戳
    DWORD PointerToSymbolTable; // 指向符号表（一般为0）
    DWORD NumberOfSymbols;      // 符号表中符号数（一般为0）
    WORD  SizeOfOptionalHeader; // 可选头大小（IMAGE_OPTIONAL_HEADER大小）
    WORD  Characteristics;      // 文件属性标志
} IMAGE_FILE_HEADER, *PIMAGE_FILE_HEADER;
```

文件头共20字节，其中有4个重要成员

1. `Machine`:表示该可执行文件针对哪种 CPU 架构编译![](C:\Users\34743\Desktop\machine.png)

2. `NumberOfSections`:文件的节区数量

3. `SizeOfOptionalHeader`:指明可选头的大小，PE文件使用`IMAGE_FILE_HEADER32`结构体，PE+文件使用`IMAGE_FILE_HEADER64`结构体

4. `Characteristics`:标识文件属性，`0x0002`代表可执行文件，`0x2000`代表是DLL文件

   | 值（十六进制） | 宏定义                                 | 含义                               |
   | -------------- | -------------------------------------- | ---------------------------------- |
   | `0x0001`       | **IMAGE_FILE_RELOCS_STRIPPED**         | 无重定位信息（地址固定）           |
   | `0x0002`       | **IMAGE_FILE_EXECUTABLE_IMAGE**        | 可执行文件（非.obj）               |
   | `0x0004`       | **IMAGE_FILE_LINE_NUMS_STRIPPED**      | 已去除行号信息（调试符号）         |
   | `0x0008`       | **IMAGE_FILE_LOCAL_SYMS_STRIPPED**     | 已去除本地符号信息                 |
   | `0x0010`       | **IMAGE_FILE_AGGRESIVE_WS_TRIM**       | Windows 95 用（过时）              |
   | `0x0020`       | **IMAGE_FILE_LARGE_ADDRESS_AWARE**     | 可使用 >2GB 地址空间（大地址感知） |
   | `0x0080`       | **IMAGE_FILE_BYTES_REVERSED_LO**       | 字节序已反转（很少见）             |
   | `0x0100`       | **IMAGE_FILE_32BIT_MACHINE**           | 32 位架构（即使在 64 位 OS 上）    |
   | `0x0200`       | **IMAGE_FILE_DEBUG_STRIPPED**          | 调试信息被移除                     |
   | `0x0400`       | **IMAGE_FILE_REMOVABLE_RUN_FROM_SWAP** | 从可移动介质运行（过时）           |
   | `0x0800`       | **IMAGE_FILE_NET_RUN_FROM_SWAP**       | 从网络运行（过时）                 |
   | `0x1000`       | **IMAGE_FILE_SYSTEM**                  | 系统文件（如驱动程序或内核模块）   |
   | `0x2000`       | **IMAGE_FILE_DLL**                     | DLL 文件                           |
   | `0x4000`       | **IMAGE_FILE_UP_SYSTEM_ONLY**          | 只能在单处理器系统上运行           |
   | `0x8000`       | **IMAGE_FILE_BYTES_REVERSED_HI**       | 字节序已反转（高位）               |

   并且可以组合，例如`0x2102`代表：可执行 (`0x0002`) + DLL (`0x2000`) + 32位架构 (`0x0100`)

#### 可选头

```c
typedef struct _IMAGE_OPTIONAL_HEADER64 {
    WORD    Magic;                     // 标识是PE32还是PE32+
    BYTE    MajorLinkerVersion;        // 链接器主版本号
    BYTE    MinorLinkerVersion;        // 链接器次版本号
    DWORD   SizeOfCode;                // 代码节总大小（.text）
    DWORD   SizeOfInitializedData;     // 已初始化数据节大小（.data）
    DWORD   SizeOfUninitializedData;   // 未初始化数据节大小（.bss）
    DWORD   AddressOfEntryPoint;       // 程序入口点RVA
    DWORD   BaseOfCode;                // 代码节起始RVA
    ULONGLONG ImageBase;               // 程序默认加载基址
    DWORD   SectionAlignment;          // 内存对齐
    DWORD   FileAlignment;             // 文件对齐
    WORD    MajorOperatingSystemVersion;
    WORD    MinorOperatingSystemVersion;
    WORD    MajorImageVersion;
    WORD    MinorImageVersion;
    WORD    MajorSubsystemVersion;
    WORD    MinorSubsystemVersion;
    DWORD   Win32VersionValue;         // 保留（一般为0）
    DWORD   SizeOfImage;               // 整个映像大小（内存对齐后）
    DWORD   SizeOfHeaders;             // 头部大小（对齐到FileAlignment）
    DWORD   CheckSum;                  // 校验和（驱动签名）
    WORD    Subsystem;                 // 子系统类型（控制台/GUI）
    WORD    DllCharacteristics;        // DLL特性标志
    ULONGLONG SizeOfStackReserve;      // 栈保留大小
    ULONGLONG SizeOfStackCommit;       // 栈提交大小
    ULONGLONG SizeOfHeapReserve;       // 堆保留大小
    ULONGLONG SizeOfHeapCommit;        // 堆提交大小
    DWORD   LoaderFlags;               // 保留（一般为0）
    DWORD   NumberOfRvaAndSizes;       // 数据目录表数量（通常为16）
    IMAGE_DATA_DIRECTORY DataDirectory[IMAGE_NUMBEROF_DIRECTORY_ENTRIES]; // 数据目录数组
} IMAGE_OPTIONAL_HEADER64, *PIMAGE_OPTIONAL_HEADER64;
```

以下值设置错误会导致文件无法正常运行

| 字段                  | 含义                                                         | 示例                     |
| --------------------- | ------------------------------------------------------------ | ------------------------ |
| `Magic`               | PE(`0x10B`) 或 PE+(`0x20B`)                                  | 0x20B 表示 64 位文件     |
| `AddressOfEntryPoint` | 程序入口点的 RVA（相对虚拟地址）                             | 0x1234                   |
| `ImageBase`           | 程序默认装载基址（64位为8字节），WindowEXE默认ImageBase值为`00400000`，DLL文件的ImageBase值为`10000000` | 0x140000000              |
| `SectionAlignment`    | 指定了节区在内存文件中最小单位（通常 0x1000）                |                          |
| `FileAlignment`       | 指定了节区在磁盘文件中最小单位（通常 0x200）                 |                          |
| `Subsystem`           | 程序运行环境                                                 | 2=Windows GUI, 3=Console |
| `DllCharacteristics`  | DLL 特性标志（见后面）                                       | 0x8160                   |
| `SizeOfImage`         | 程序整体映像大小（内存中）                                   | 0x56000                  |
| `SizeOfHeaders`       | 整个PE头大小，该值必须是`FileAlignment`的整数倍              | 0x400                    |
| `NumberOfRvaAndSizes` | 数据目录数量（通常16）                                       | 16                       |

`DllCharacteristics`常见值汇总

| 标志名                                           | 十六进制值 | 说明                                        | 典型影响 / 用途                          |
| ------------------------------------------------ | ---------- | ------------------------------------------- | ---------------------------------------- |
| `IMAGE_DLLCHARACTERISTICS_HIGH_ENTROPY_VA`       | `0x0020`   | 支持高熵地址空间随机化（High Entropy ASLR） | 针对 64 位程序的更强随机化，提高防利用性 |
| `IMAGE_DLLCHARACTERISTICS_DYNAMIC_BASE`          | `0x0040`   | 支持重定位（ASLR）                          | 允许系统在加载时随机调整映像基址         |
| `IMAGE_DLLCHARACTERISTICS_FORCE_INTEGRITY`       | `0x0080`   | 强制签名完整性检查                          | 系统仅加载具有正确签名的映像             |
| `IMAGE_DLLCHARACTERISTICS_NX_COMPAT`             | `0x0100`   | 支持 DEP（Data Execution Prevention）       | 防止在数据页执行代码                     |
| `IMAGE_DLLCHARACTERISTICS_NO_ISOLATION`          | `0x0200`   | 不使用程序集隔离（No Side-by-Side）         | 禁止使用 SxS 机制，常用于老程序          |
| `IMAGE_DLLCHARACTERISTICS_NO_SEH`                | `0x0400`   | 映像中不包含结构化异常处理（SEH）           | 防止异常表利用，常见于安全强化的程序     |
| `IMAGE_DLLCHARACTERISTICS_NO_BIND`               | `0x0800`   | 禁止绑定导入表                              | 系统不会预先计算导入表的地址             |
| `IMAGE_DLLCHARACTERISTICS_APPCONTAINER`          | `0x1000`   | 必须在 AppContainer 中运行                  | 用于 UWP 或受限沙盒环境                  |
| `IMAGE_DLLCHARACTERISTICS_WDM_DRIVER`            | `0x2000`   | 表示 WDM 驱动程序                           | 驱动程序加载时使用的标志                 |
| `IMAGE_DLLCHARACTERISTICS_GUARD_CF`              | `0x4000`   | 支持 Control Flow Guard (CFG)               | 防止间接调用跳转攻击（ROP/JOP）          |
| `IMAGE_DLLCHARACTERISTICS_TERMINAL_SERVER_AWARE` | `0x8000`   | 兼容终端服务（Remote Desktop）              | 程序可在多用户环境下正常运行             |

`Subsystem`取值

| 值   | 宏定义                                     | 含义               |
| ---- | ------------------------------------------ | ------------------ |
| 1    | `IMAGE_SUBSYSTEM_NATIVE`                   | 内核驱动/系统程序  |
| 2    | `IMAGE_SUBSYSTEM_WINDOWS_GUI`              | Windows GUI 程序   |
| 3    | `IMAGE_SUBSYSTEM_WINDOWS_CUI`              | Windows 控制台程序 |
| 9    | `IMAGE_SUBSYSTEM_WINDOWS_CE_GUI`           | Windows CE 程序    |
| 10   | `IMAGE_SUBSYSTEM_EFI_APPLICATION`          | EFI 应用           |
| 11   | `IMAGE_SUBSYSTEM_EFI_BOOT_SERVICE_DRIVER`  | EFI 启动驱动       |
| 14   | `IMAGE_SUBSYSTEM_XBOX`                     | Xbox 应用          |
| 16   | `IMAGE_SUBSYSTEM_WINDOWS_BOOT_APPLICATION` | 启动管理器程序     |

数据目录

```c
typedef struct _IMAGE_DATA_DIRECTORY {
    DWORD VirtualAddress; // RVA：相对虚拟地址
    DWORD Size;           // 该数据结构的大小（字节）
} IMAGE_DATA_DIRECTORY, *PIMAGE_DATA_DIRECTORY;
```

也就是说，每一项都只占 **8 个字节**：

- 前 4 字节 = 表在内存中的相对地址（RVA）
- 后 4 字节 = 该表的长度

DataDirectory 数组内容

| 索引   | 宏定义                                 | 表名                                    | 作用 / 内容描述                                            |
| ------ | -------------------------------------- | --------------------------------------- | ---------------------------------------------------------- |
| **0**  | `IMAGE_DIRECTORY_ENTRY_EXPORT`         | **导出表 (Export Table)**               | 存放本模块导出的函数、符号、变量等信息（DLL最关键）        |
| **1**  | `IMAGE_DIRECTORY_ENTRY_IMPORT`         | **导入表 (Import Table)**               | 记录本模块从哪些DLL导入了哪些API函数                       |
| **2**  | `IMAGE_DIRECTORY_ENTRY_RESOURCE`       | **资源表 (Resource Table)**             | 包含图标、菜单、对话框、字符串等资源数据                   |
| **3**  | `IMAGE_DIRECTORY_ENTRY_EXCEPTION`      | **异常表 (Exception Table)**            | 保存异常处理/函数展开信息（特别是x64）                     |
| **4**  | `IMAGE_DIRECTORY_ENTRY_SECURITY`       | **安全表 (Security/Certificate Table)** | 数字签名（Authenticode）的位置（文件偏移）                 |
| **5**  | `IMAGE_DIRECTORY_ENTRY_BASERELOC`      | **重定位表 (Base Relocation Table)**    | 存放重定位块，用于ASLR基址变化修复地址                     |
| **6**  | `IMAGE_DIRECTORY_ENTRY_DEBUG`          | **调试表 (Debug Directory)**            | 指向调试信息（如PDB路径、时间戳）                          |
| **7**  | `IMAGE_DIRECTORY_ENTRY_ARCHITECTURE`   | 架构特定表                              | 为将来扩展保留，基本未用                                   |
| **8**  | `IMAGE_DIRECTORY_ENTRY_GLOBALPTR`      | 全局指针寄存器表                        | MIPS架构专用（在x86/x64中未用）                            |
| **9**  | `IMAGE_DIRECTORY_ENTRY_TLS`            | **TLS 表 (Thread Local Storage)**       | 保存线程本地存储区的信息（C/C++中的 `__declspec(thread)`） |
| **10** | `IMAGE_DIRECTORY_ENTRY_LOAD_CONFIG`    | **加载配置表 (Load Config Table)**      | 含安全相关信息，如SafeSEH, CFG, Guard Flags                |
| **11** | `IMAGE_DIRECTORY_ENTRY_BOUND_IMPORT`   | **绑定导入表 (Bound Import Table)**     | 优化导入速度的静态绑定信息                                 |
| **12** | `IMAGE_DIRECTORY_ENTRY_IAT`            | **导入地址表 (Import Address Table)**   | 加载时动态重写的IAT数组（每个API最终地址）                 |
| **13** | `IMAGE_DIRECTORY_ENTRY_DELAY_IMPORT`   | **延迟导入表 (Delay Import Table)**     | 延迟加载DLL时使用                                          |
| **14** | `IMAGE_DIRECTORY_ENTRY_COM_DESCRIPTOR` | **CLR 表 (COM Descriptor Table)**       | .NET程序特有，指向CLR头结构                                |
| **15** | 保留                                   | 未使用                                  | 未来扩展                                                   |

### 节区头

```c
typedef struct _IMAGE_SECTION_HEADER {
    BYTE  Name[8];                // 节区名称（例如 ".text"、".data" 等）
    union {
        DWORD PhysicalAddress;
        DWORD VirtualSize;        // 节区实际在内存中的大小
    } Misc;
    DWORD VirtualAddress;         // 节区加载到内存后的 RVA
    DWORD SizeOfRawData;          // 节区在文件中的实际大小（磁盘中的大小）
    DWORD PointerToRawData;       // 节区在文件中的偏移（文件偏移地址）
    DWORD PointerToRelocations;   // 重定位表的偏移（仅用于目标文件 .obj）
    DWORD PointerToLinenumbers;   // 行号表偏移（仅用于目标文件 .obj）
    WORD  NumberOfRelocations;    // 重定位项数量
    WORD  NumberOfLinenumbers;    // 行号项数量
    DWORD Characteristics;        // 节区属性标志（读写执行等）
} IMAGE_SECTION_HEADER, *PIMAGE_SECTION_HEADER;

```

`VirtualAddress`和`PointerToRawData`不带有任何值，分别由`SectionAlignment`和`FileAlignment`确定

> PE文件总结的思维导图：通过网盘分享的文件：PE文件.png
> 链接: https://pan.baidu.com/s/1nLxhTmPN_OwETmGCDs_8hA?pwd=flag 提取码: flag 

## 磁盘与内存映射

磁盘：**持久存储设备**，比如硬盘（HDD）、固态硬盘（SSD）等

内存：CPU 在运行时访问的**临时工作空间**（RAM，随机存取存储器）

| 名称           | 英文全称                 | 所属环境 | 含义                                          |
| -------------- | ------------------------ | -------- | --------------------------------------------- |
| **RAW Offset** | File Offset              | 磁盘文件 | 在文件中的**字节偏移量**（从文件开头算）      |
| **VA**         | Virtual Address          | 内存     | 加载到内存后的**绝对虚拟地址**                |
| **RVA**        | Relative Virtual Address | 内存     | 相对于 `ImageBase` 的偏移量：`VA - ImageBase` |

PE文件**加载到内存**时，每个节区都要完成内存地址与文件偏移间的映射，成为`RVA to RAW `

RVA to RAW公式：

`RAW = (RVA - Section[i].VirtualAddress) + Section[i].PointerToRawData`

