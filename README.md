# analysis-skidonion

`.diy` native 库打包机制的复刻仓库。

本仓库不存放任何实际样本、样本指纹、样本内路径/类名或反编译代码；文档
只描述算法，可复刻产物由脚本现场生成，示例 DLL 由 C++ + xmake 构建。

## 算法描述

### 打包（生产 `.diy`）

1. 取输入文件（PE / ELF / Mach-O 均可）全文；
2. 目标平台后缀为 `.diy` 时，将前 `min(1024, len)` 字节**逐字节
   `XOR 1`**；
3. 写出加密内容后**追加诱饵**：
   - 若干行 `TXT<0-99>\n` 随机文本（复刻默认 100 行）；
   - 一个 zip，内含 `data.txt`（若干行 `DIY<0-99>\n`，复刻默认 100 行）；
4. 诱饵位于镜像末尾、PE 节表之外，Windows 加载器按节表映射，尾部数据
   被忽略，不影响 `LoadLibrary`。

### 解包（还原）

1. 检测尾部诱饵（连续 `TXT<n>\n` 行 + 可解析的 zip），有则剥离；
2. 将前 `min(1024, len)` 字节再次 `XOR 1`，即得原始文件。

加密只作用于文件头部 1024 字节且与追加内容互不重叠，因此还原**无损**、
可往返验证。

## 仓库内容

| 路径 | 说明 |
| --- | --- |
| `pack_diy.py` | 生产 `.diy` 容器（XOR + 诱饵追加） |
| `unpack_diy.py` | 还原原始文件（剥诱饵 + XOR） |
| `native/` | C++ + xmake 示例 DLL，作为 `.diy` 载荷 |

## 使用

```sh
# 1. 构建示例载荷 DLL
cd native && xmake && cd ..

# 2. 生产 .diy
python pack_diy.py native/build/windows/x64/release/diy_payload.dll out.diy

# 3. 还原并校验往返一致
python unpack_diy.py out.diy restored.dll
```

`pack_diy.py --seed <n>` 可固定诱饵随机数以便复现同一产物；`--no-junk`
只输出 XOR 部分（即仅头部加密、不带诱饵的变体）。

## 边界声明

- 文档仅描述算法，不含原始代码片段；
- 不提交任何 `.diy` / `.dll` 生成物（`.gitignore` 已排除）；
- 实际样本的分析与证据只存在于本地隔离的分析目录，不进入本仓库。
