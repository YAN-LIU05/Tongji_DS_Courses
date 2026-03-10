#!/bin/bash

# 设置环境变量
PYTHON_PATH=python
DATASET_PATH=./data
CKPT_PATH=./pretrain_checkpoint/mobilenetv2_cpu_gpu.ckpt
FREEZE_LAYER=backbone
PLATFORM=CPU

# 检查数据集目录
if [ ! -d "${DATASET_PATH}/train" ]; then
    echo "错误: 训练数据集未找到: ${DATASET_PATH}/train"
    exit 1
fi

# 检查预训练模型
if [ ! -f "${CKPT_PATH}" ]; then
    echo "错误: 预训练模型未找到: ${CKPT_PATH}"
    exit 1
fi

echo "开始 MobileNetV2 训练..."

$PYTHON_PATH code/train.py \
    --platform "$PLATFORM" \
    --dataset_path "$DATASET_PATH" \
    --pretrain_ckpt "$CKPT_PATH" \
    --freeze_layer "$FREEZE_LAYER"

if [ $? -ne 0 ]; then
    echo "训练失败！"
else
    echo "训练完成！"
fi

read -p "按任意键退出..."
