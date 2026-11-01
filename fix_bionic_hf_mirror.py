#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Bionic / LM Studio 「探索」页 Hugging Face 搜索失败 —— 一键修复

原理：Bionic 主进程把所有 HF 请求地址硬编码在 JS 里（不读 HF_ENDPOINT 环境变量），
      useHFProxy=true 走写死的 LM Studio 自家代理（国内时通时不通），
      false 直连 huggingface.co（国内超时）。本脚本把这些地址改指国内镜像
      hf-mirror.com，搜索 / 模型元数据 / 下载统一走镜像。

用法：完全退出 Bionic（托盘图标也关掉）后运行：
          python C:\\Users\\27674\\.workbuddy\\fix_bionic_hf_mirror.py
      跑完重新打开 Bionic，进「探索」搜索验证。

回滚：把同目录生成的 *.js.bak 去掉 .bak 覆盖回原文件即可。

幂等：已是镜像版会跳过；Bionic 更新把文件覆盖回原始版后，重跑会自动刷新备份。
"""
import os
import shutil
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE = r"D:\Program Files\Bionic\resources\app\.webpack-bionic"
NODE = os.path.join(BASE, "bin", "node.exe")
FILES = [
    os.path.join("main", "index.js"),
    os.path.join("renderer", "main_window.js"),
]
REPLACEMENTS = [
    (b"https://huggingface.co", b"https://hf-mirror.com"),
    (b"https://search.lmstudio.ai:443/v1/hf-proxy", b"https://hf-mirror.com"),
]


def main():
    if not os.path.isdir(BASE):
        sys.exit("[X] 找不到 Bionic 目录，请确认安装路径:\n   " + BASE)

    for rel in FILES:
        path = os.path.join(BASE, rel)
        if not os.path.exists(path):
            sys.exit("[X] 文件不存在: " + path)

        data = open(path, "rb").read()
        hits = sum(data.count(old) for old, _ in REPLACEMENTS)
        if hits == 0:
            print("[=] %s：已是镜像版，跳过" % rel)
            continue

        bak = path + ".bak"
        # 备份逻辑：无备份则创建；若已有备份但当前文件被更新覆盖回原始版
        #（含 huggingface.co），说明版本变了，刷新备份以保证回滚到当前原始版。
        if not os.path.exists(bak):
            shutil.copy2(path, bak)
            print("[备份] %s -> %s" % (rel, os.path.basename(bak)))
        elif b"https://huggingface.co" in data:
            shutil.copy2(path, bak)
            print("[备份] %s：检测到更新后的原始版，已刷新备份" % rel)
        else:
            print("[备份] %s：已有备份，保留" % rel)

        for old, new in REPLACEMENTS:
            n = data.count(old)
            if n:
                data = data.replace(old, new)
                print("   替换 %s -> %s : %d 处" % (old.decode(), new.decode(), n))
        with open(path, "wb") as f:
            f.write(data)

        if os.path.exists(NODE):
            r = subprocess.run([NODE, "--check", path], capture_output=True, text=True)
            print("   语法校验: %s" % ("OK" if r.returncode == 0 else "FAIL " + (r.stderr or "").strip()))
        else:
            print("   语法校验: 跳过（未找到 node.exe）")

    print("\n完成。请完全退出 Bionic（托盘也关）后重新打开，进「探索」搜索验证。")
    print("回滚：同目录 *.js.bak 去掉 .bak 覆盖回原文件。")


if __name__ == "__main__":
    main()
