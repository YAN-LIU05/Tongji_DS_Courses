"""
数据预处理脚本 - 划分训练集、验证集、测试集
"""
import os
import shutil
from sklearn.model_selection import train_test_split
from tqdm import tqdm
import config

def preprocess_data():
    print("="*60)
    print("开始数据预处理")
    print("="*60)
    
    # 检查原始数据目录
    if not os.path.exists(config.RAW_DATA_DIR):
        print(f"错误: 原始数据目录不存在 {config.RAW_DATA_DIR}")
        print(f"请将你的113062张验证码图片放入 {config.RAW_DATA_DIR} 目录")
        return
    
    # 获取所有图片文件
    all_files = [f for f in os.listdir(config.RAW_DATA_DIR) 
                 if f.endswith('.jpg') or f.endswith('.png')]
    
    print(f"找到 {len(all_files)} 个图片文件")
    
    # 过滤出5位验证码
    valid_files = []
    for f in all_files:
        label = os.path.splitext(f)[0]
        if len(label) == 5:
            valid_files.append(f)
    
    print(f"有效的5位验证码数量: {len(valid_files)}")
    
    if len(valid_files) == 0:
        print("错误: 没有找到有效的5位验证码图片")
        return
    
    # 划分数据集
    train_files, temp_files = train_test_split(
        valid_files, 
        test_size=(1 - config.TRAIN_RATIO), 
        random_state=42
    )
    
    val_files, test_files = train_test_split(
        temp_files, 
        test_size=config.TEST_RATIO / (config.VAL_RATIO + config.TEST_RATIO),
        random_state=42
    )
    
    print(f"\n数据集划分:")
    print(f"  训练集: {len(train_files)} ({len(train_files)/len(valid_files)*100:.1f}%)")
    print(f"  验证集: {len(val_files)} ({len(val_files)/len(valid_files)*100:.1f}%)")
    print(f"  测试集: {len(test_files)} ({len(test_files)/len(valid_files)*100:.1f}%)")
    
    # 创建目录并复制文件
    for split_name, files in [('train', train_files), ('val', val_files), ('test', test_files)]:
        split_dir = os.path.join(config.DATA_DIR, split_name)
        os.makedirs(split_dir, exist_ok=True)
        
        print(f"\n复制文件到 {split_name} 目录...")
        for f in tqdm(files):
            src = os.path.join(config.RAW_DATA_DIR, f)
            dst = os.path.join(split_dir, f)
            shutil.copy2(src, dst)
    
    print("\n数据预处理完成！")
    print("="*60)

if __name__ == '__main__':
    preprocess_data()