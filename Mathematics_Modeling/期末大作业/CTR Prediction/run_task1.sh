#!/bin/bash

# 1. 解压transformers.zip，下载地址https://github.com/huggingface/transformers
ZIP_FILE="transformers-main.zip"
LOCAL_PACKAGE_DIR="transformers-main"
REQUIREMENTS_FILE="requirements.txt"

if [ ! -f "$ZIP_FILE" ]; then
    echo "错误：文件 $ZIP_FILE 不存在"
    exit 1
fi

echo "正在解压 $ZIP_FILE ..."
unzip -o "$ZIP_FILE"
echo "解压完成！"

# 2. 安装本地transformers包
echo "正在安装本地包..."
cd $LOCAL_PACKAGE_DIR
pip install .
cd ..

# 3. 安装依赖
if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "正在通过requirements.txt安装依赖..."
    pip install -r $REQUIREMENTS_FILE
else
    echo "错误: requirements.txt文件不存在"
    exit 1
fi

echo "依赖安装完成！"

# 4. 获取嵌入向量
echo "正在运行嵌入向量生成脚本: inference_optimized_v2.py"
python inference_optimized_v2.py
if [ $? -ne 0 ]; then
    echo "inference_optimized_v2.py 执行失败"
    exit 1
fi

# 5. 生成 item_info
echo "正在生成 item_info: gen_item_info.py"
python gen_item_info.py
if [ $? -ne 0 ]; then
    echo "gen_item_info.py 执行失败"
    exit 1
fi

# 6. 训练 DIN 并参数调优
CONFIG_FILE="config/DIN_microlens_mmctr_tuner_config_01.yaml"
GPU_ID=0
echo "正在训练 DIN 并参数调优: run_param_tuner.py"
python run_param_tuner.py --config $CONFIG_FILE --gpu $GPU_ID
if [ $? -ne 0 ]; then
    echo "run_param_tuner.py 执行失败"
    exit 1
fi

echo "全部流程执行完毕