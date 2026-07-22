#!/bin/bash

# 创建 data 目录（如果不存在）
mkdir -p data

# 检查 data 目录是否为空，如果为空则下载数据
if [ -z "$(ls -A data)" ]; then
    echo "正在下载数据..."
    cd data
    wget -r -np -nH --cut-dirs=1 http://recsys.westlake.edu.cn/MicroLens_1M_MMCTR/MicroLens_1M_x1/
    cd ..
else
    echo "data 目录非空，跳过数据下载。"
fi

# 运行实验
echo "正在运行实验..."
python run_expid.py

echo "