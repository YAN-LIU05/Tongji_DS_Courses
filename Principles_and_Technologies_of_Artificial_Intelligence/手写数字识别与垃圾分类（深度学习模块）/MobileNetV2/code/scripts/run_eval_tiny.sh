#!/bin/bash

set -e

PYTHON_PATH=python
DATASET_PATH=./data_new
CKPT_PATH=./ckpt_0/mobilenetv2_100.ckpt
PLATFORM=CPU

echo "开始模型验证..."

$PYTHON_PATH code/eval.py \
    --platform "$PLATFORM" \
    --dataset_path "$DATASET_PATH" \
    --pretrain_ckpt "$CKPT_PATH"

if [ $? -ne 0 ]; then
    echo "验证失败！"
else
    echo "验证完成！"
fi

read -p "按任意键退出..."
