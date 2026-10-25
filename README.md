# analysis-skidonion

`.diy` native 库打包机制的复刻仓库：容器生产/还原脚本，以及由
C++ + xmake 构建的示例载荷。

算法细节见 [diy-format.md](diy-format.md)。

## 仓库内容

| 路径 | 说明 |
| --- | --- |
| `diy-format.md` | 算法描述（容器布局、打包、解包） |
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
