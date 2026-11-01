# lm-studio-tools

LM Studio / Bionic 的修复与调优脚本集合。

## fix_bionic_hf_mirror.py

**用途**：一键修复 Bionic（LM Studio）「探索」页 Hugging Face 搜索失败的问题。

**背景**：Bionic 主进程把所有 HF 请求地址硬编码在 JS 里（不读 `HF_ENDPOINT` 环境变量）。
`useHFProxy=true` 时走写死的 LM Studio 自家代理（国内时通时不通），`false` 时直连
`huggingface.co`（国内超时）。本脚本把这些地址改指国内镜像 `hf-mirror.com`，
让搜索 / 模型元数据 / 下载统一走镜像。

**用法**：完全退出 Bionic（托盘图标也关掉）后运行：

```powershell
python C:\Users\27674\.workbuddy\fix_bionic_hf_mirror.py
```

跑完重新打开 Bionic，进「探索」搜索验证。

**回滚**：把同目录生成的 `*.js.bak` 去掉 `.bak` 覆盖回原文件即可。

**特性**：
- 幂等：已是镜像版会跳过；Bionic 更新把文件覆盖回原始版后，重跑会自动刷新备份。
- 每次替换都会用 `node --check` 做语法校验。

## 环境说明

- 适用：Windows + Bionic / LM Studio（安装路径 `D:\Program Files\Bionic\...`）
- 需要：Python 3 + Bionic 自带的 node.exe（脚本会自动调用做语法校验）
