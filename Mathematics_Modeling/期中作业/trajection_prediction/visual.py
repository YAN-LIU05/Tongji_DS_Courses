import matplotlib.pyplot as plt
import pandas as pd
import os
import numpy as np
from datetime import datetime


def parse_trajectory_file(file_path):
    """解析轨迹文件"""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None

    data = []
    with open(file_path, 'r') as f:
        line_num = 0
        for line in f:
            line = line.strip()
            if line == 'MASK':
                data.append({'timestamp': None, 'lon': np.nan, 'lat': np.nan, 'mask': True, 'line_num': line_num})
            else:
                try:
                    parts = line.split(',')
                    timestamp = datetime.strptime(parts[0], '%Y-%m-%d %H:%M:%S')
                    lon = float(parts[1])
                    lat = float(parts[2])
                    data.append({'timestamp': timestamp, 'lon': lon, 'lat': lat, 'mask': False, 'line_num': line_num})
                except Exception as e:
                    print(f"Parse error (line {line_num}): {line}, Error: {e}")
            line_num += 1

    if not data:
        return None

    return pd.DataFrame(data)


def visualize_predictions(pred_dir, masked_dir, true_dir, output_dir='trajectory_visualizations'):
    """可视化预测结果与原始/真实轨迹对比"""
    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 获取预测文件列表
    pred_files = os.listdir(pred_dir)
    total_files = len(pred_files)
    print(f"Found {total_files} prediction files, generating visualizations...")

    # 可视化每个文件
    for i, file_name in enumerate(pred_files):
        print(f"Processing file ({i + 1}/{total_files}): {file_name}")

        # 文件路径
        pred_path = os.path.join(pred_dir, file_name)
        masked_path = os.path.join(masked_dir, file_name)
        true_path = os.path.join(true_dir, file_name) if true_dir and os.path.exists(
            os.path.join(true_dir, file_name)) else None

        # 解析文件
        pred_df = parse_trajectory_file(pred_path)
        masked_df = parse_trajectory_file(masked_path)
        true_df = parse_trajectory_file(true_path) if true_path else None

        if pred_df is None or masked_df is None:
            print(f"  Warning: Cannot parse file {file_name}, skipping")
            continue

        # 创建图形
        plt.figure(figsize=(10, 8))

        # 绘制掩码轨迹中的非掩码点
        if masked_df is not None:
            non_mask = masked_df[~masked_df['mask'].fillna(False)]
            if not non_mask.empty:
                plt.plot(non_mask['lon'], non_mask['lat'], 'o', color='blue', markersize=4, alpha=0.7,
                         label='Original Points')

            # 标记掩码点位置
            mask_points = masked_df[masked_df['mask'].fillna(False)]
            if not mask_points.empty:
                for _, point in mask_points.iterrows():
                    if 'line_num' in point:
                        plt.text(non_mask['lon'].mean(), non_mask['lat'].min() - 0.0001,
                                 f"Mask Points: {len(mask_points)}", color='red', fontsize=10)
                        break

        # 绘制真实轨迹
        if true_df is not None:
            plt.plot(true_df['lon'], true_df['lat'], '-', color='green', linewidth=2, alpha=0.7,
                     label='True Trajectory')

        # 绘制预测轨迹
        if pred_df is not None:
            plt.plot(pred_df['lon'], pred_df['lat'], '-', color='red', linewidth=2, label='Predicted Trajectory')

        # 设置图形属性
        plt.title(f'Trajectory Prediction: {file_name}', fontsize=14)
        plt.xlabel('Longitude', fontsize=12)
        plt.ylabel('Latitude', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend(loc='best')

        # 保存图形
        img_path = os.path.join(output_dir, f'{os.path.splitext(file_name)[0]}.png')
        plt.tight_layout()
        plt.savefig(img_path, dpi=150)
        plt.close()

    print(f"\nVisualization complete! Processed {total_files} files")
    print(f"Results saved to: {output_dir}")


# 配置目录
train_dir = 'train'  # 真实轨迹
train_masked_dir = 'train_masked'  # 掩码轨迹
train_pred_dir = 'train_predictions'  # 预测结果

# 执行可视化
visualize_predictions(train_pred_dir, train_masked_dir, train_dir, 'train_visualizations')