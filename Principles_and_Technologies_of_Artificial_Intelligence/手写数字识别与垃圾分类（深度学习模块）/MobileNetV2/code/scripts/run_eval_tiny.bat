@echo off
setlocal

set PYTHON_PATH=python
set DATASET_PATH=.\data_new
set CKPT_PATH=.\ckpt_0\mobilenetv2_100.ckpt
set PLATFORM=CPU

echo 开始模型验证...

%PYTHON_PATH% code/eval.py ^
    --platform %PLATFORM% ^
    --dataset_path %DATASET_PATH% ^
    --pretrain_ckpt %CKPT_PATH%

if errorlevel 1 (
    echo 验证失败！
) else (
    echo 验证完成！
)

pause