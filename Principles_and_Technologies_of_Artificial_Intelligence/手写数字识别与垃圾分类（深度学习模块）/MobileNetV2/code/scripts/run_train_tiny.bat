@echo off
setlocal enabledelayedexpansion

:: 设置环境变量
set PYTHON_PATH=python
set DATASET_PATH=.\data
set CKPT_PATH=.\pretrain_checkpoint\mobilenetv2_cpu_gpu.ckpt
set FREEZE_LAYER=backbone
set PLATFORM=CPU

:: 检查数据集目录
if not exist "%DATASET_PATH%\train" (
    echo 错误: 训练数据集未找到: %DATASET_PATH%\train
    exit /b 1
)

:: 检查预训练模型
if not exist "%CKPT_PATH%" (
    echo 错误: 预训练模型未找到: %CKPT_PATH%
    exit /b 1
)

echo 开始 MobileNetV2 训练...

%PYTHON_PATH% code/train.py ^
    --platform %PLATFORM% ^
    --dataset_path %DATASET_PATH% ^
    --pretrain_ckpt %CKPT_PATH% ^
    --freeze_layer %FREEZE_LAYER%

if errorlevel 1 (
    echo 训练失败！
) else (
    echo 训练完成！
)

pause