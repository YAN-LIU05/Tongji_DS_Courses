import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.metrics import mean_squared_error
import similaritymeasures
import matplotlib.pyplot as plt
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw
from sklearn.metrics import mean_squared_error, mean_absolute_error
import math
from scipy.signal import savgol_filter

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def haversine(lon1, lat1, lon2, lat2):
    """
    计算两点之间的 Haversine 距离（单位：米）。
    参数：
        lon1, lat1: 第一点的经纬度（度）
        lon2, lat2: 第二点的经纬度（度）
    返回：
        距离（米）
    """
    R = 6371000
    phi1 = np.radians(lat1)
    phi2 = np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lon2 - lon1)
    a = np.sin(delta_phi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(delta_lambda / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    distance = R * c
    return distance

def calculate_trajectory_features(df):
    """为轨迹点计算速度、方向和曲率特征，使用 Haversine 距离"""
    df = df.copy()
    df['speed'] = np.nan
    df['direction'] = np.nan
    df['curvature'] = np.nan

    valid_points = df[~df['mask'] & df['lon'].notna() & df['lat'].notna()]
    valid_indices = valid_points.index.tolist()

    if len(valid_indices) < 2:
        return df

    # 计算速度和方向
    for i in range(len(valid_indices) - 1):
        idx1 = valid_indices[i]
        idx2 = valid_indices[i + 1]

        if pd.notna(df.at[idx1, 'timestamp']) and pd.notna(df.at[idx2, 'timestamp']):
            time_diff = (df.at[idx2, 'timestamp'] - df.at[idx1, 'timestamp']).total_seconds()
            if time_diff > 0:
                dist = haversine(df.at[idx1, 'lon'], df.at[idx1, 'lat'],
                                df.at[idx2, 'lon'], df.at[idx2, 'lat'])
                df.at[idx2, 'speed'] = dist / time_diff

                delta_lon = df.at[idx2, 'lon'] - df.at[idx1, 'lon']
                delta_lat = df.at[idx2, 'lat'] - df.at[idx1, 'lat']
                direction = np.arctan2(delta_lon, delta_lat) * 180 / np.pi
                if direction < 0:
                    direction += 360
                df.at[idx2, 'direction'] = direction

    # 计算曲率（需要至少3个点）
    if len(valid_indices) >= 3:
        for i in range(1, len(valid_indices) - 1):
            idx1 = valid_indices[i - 1]
            idx2 = valid_indices[i]
            idx3 = valid_indices[i + 1]

            p1 = (df.at[idx1, 'lon'], df.at[idx1, 'lat'])
            p2 = (df.at[idx2, 'lon'], df.at[idx2, 'lat'])
            p3 = (df.at[idx3, 'lon'], df.at[idx3, 'lat'])

            try:
                d1 = haversine(p1[0], p1[1], p2[0], p2[1])
                d2 = haversine(p2[0], p2[1], p3[0], p3[1])
                d3 = haversine(p1[0], p1[1], p3[0], p3[1])

                if d1 > 0 and d2 > 0 and d3 > 0:
                    cos_angle = (d1**2 + d2**2 - d3**2) / (2 * d1 * d2)
                    if -1 < cos_angle < 1:
                        sin_angle = np.sqrt(1 - cos_angle**2)
                        curvature = 2 * sin_angle / (d1 + d2)
                        df.at[idx2, 'curvature'] = curvature
            except Exception:
                continue

    df['speed'] = df['speed'].interpolate(method='linear').bfill().ffill()
    df['direction'] = df['direction'].interpolate(method='linear').bfill().ffill()
    df['curvature'] = df['curvature'].interpolate(method='linear').bfill().ffill()

    return df

# GPS坐标数据清洗与预处理
def clean_gps_data(df):
    cleaned_df = df.copy()
    valid_points = cleaned_df[~cleaned_df['mask']]

    if len(valid_points) <= 2:
        return cleaned_df

    # 1. 去除经纬度异常值（Z-score方法）
    lon_mean, lon_std = valid_points['lon'].mean(), valid_points['lon'].std()
    lat_mean, lat_std = valid_points['lat'].mean(), valid_points['lat'].std()

    if lon_std > 0 and lat_std > 0:
        z_threshold = 3.0
        for idx in valid_points.index:
            lon_z = abs((cleaned_df.at[idx, 'lon'] - lon_mean) / lon_std)
            lat_z = abs((cleaned_df.at[idx, 'lat'] - lat_mean) / lat_std)
            if lon_z > z_threshold or lat_z > z_threshold:
                cleaned_df.at[idx, 'mask'] = True
                cleaned_df.at[idx, 'lon'] = np.nan
                cleaned_df.at[idx, 'lat'] = np.nan

    # 2. 速度异常检测
    if len(valid_points) >= 3:
        speeds = []
        valid_indices = valid_points.index.tolist()
        for i in range(len(valid_indices) - 1):
            idx1 = valid_indices[i]
            idx2 = valid_indices[i + 1]
            if (pd.notna(cleaned_df.at[idx1, 'timestamp']) and
                pd.notna(cleaned_df.at[idx2, 'timestamp']) and
                pd.notna(cleaned_df.at[idx1, 'lon']) and
                pd.notna(cleaned_df.at[idx1, 'lat']) and
                pd.notna(cleaned_df.at[idx2, 'lon']) and
                pd.notna(cleaned_df.at[idx2, 'lat'])):
                dist = np.sqrt((cleaned_df.at[idx2, 'lon'] - cleaned_df.at[idx1, 'lon']) ** 2 +
                              (cleaned_df.at[idx2, 'lat'] - cleaned_df.at[idx1, 'lat']) ** 2)
                time_diff = (cleaned_df.at[idx2, 'timestamp'] - cleaned_df.at[idx1, 'timestamp']).total_seconds()
                if time_diff > 0:
                    speed = dist / time_diff
                    speeds.append((idx2, speed))
        if speeds:
            speed_values = [s[1] for s in speeds]
            q1 = np.percentile(speed_values, 25)
            q3 = np.percentile(speed_values, 75)
            iqr = q3 - q1
            speed_threshold = q3 + 1.5 * iqr
            for idx, speed in speeds:
                if speed > speed_threshold:
                    cleaned_df.at[idx, 'mask'] = True
                    cleaned_df.at[idx, 'lon'] = np.nan
                    cleaned_df.at[idx, 'lat'] = np.nan

    # 3. 平滑处理（Savitzky-Golay滤波器）
    valid_points = cleaned_df[~cleaned_df['mask']]
    if len(valid_points) >= 5:
        lon_values = valid_points['lon'].values
        lat_values = valid_points['lat'].values
        try:
            window_length = min(5, len(valid_points) - (len(valid_points) % 2 == 0))
            if window_length > 2:
                smoothed_lon = savgol_filter(lon_values, window_length, 2)
                smoothed_lat = savgol_filter(lat_values, window_length, 2)
                for i, idx in enumerate(valid_points.index):
                    cleaned_df.at[idx, 'lon'] = smoothed_lon[i]
                    cleaned_df.at[idx, 'lat'] = smoothed_lat[i]
        except Exception as e:
            print(f"  平滑处理时出错: {e}")

    return cleaned_df

def get_mask_positions(file_path):
    mask_line_numbers = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            line_num = 0
            while True:
                line = f.readline()
                if not line:
                    break
                line = line.strip()
                if line == 'MASK':
                    mask_line_numbers.append(line_num)
                line_num += 1
    except Exception as e:
        print(f"  错误: 读取MASK位置失败 {file_path}: {e}")
    return mask_line_numbers

def parse_trajectory(file_path):
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            line_num = 0
            for line in f:
                line = line.strip()
                try:
                    if line == 'MASK':
                        data.append(
                            {'timestamp': None, 'lon': np.nan, 'lat': np.nan, 'mask': True, 'line_num': line_num})
                    else:
                        parts = line.split(',')
                        if len(parts) < 3:
                            print(f"  警告: 行 {line_num} 格式错误 '{line}'，跳过该行")
                            continue
                        try:
                            timestamp = datetime.strptime(parts[0], '%Y-%m-%d %H:%M:%S')
                            lon = float(parts[1])
                            lat = float(parts[2])
                            data.append(
                                {'timestamp': timestamp, 'lon': lon, 'lat': lat, 'mask': False, 'line_num': line_num})
                        except ValueError as e:
                            print(f"  警告: 行 {line_num} 数据转换错误 '{line}': {e}，跳过该行")
                            continue
                except Exception as e:
                    print(f"  警告: 处理行 {line_num} 时出错: {e}，跳过该行")
                    continue
                line_num += 1
    except Exception as e:
        print(f"  错误: 无法读取文件 {file_path}: {e}")
        return pd.DataFrame()

    if not data:
        print(f"  警告: 文件 {file_path} 中没有找到有效数据")
        return pd.DataFrame()

    df = pd.DataFrame(data)
    if df.empty:
        return df

    # 分配时间戳
    mask_indices = df[df['mask']].index
    for idx in mask_indices:
        try:
            prev_points = df.iloc[:idx][~df.iloc[:idx]['mask']]
            next_points = df.iloc[idx + 1:][~df.iloc[idx + 1:]['mask']]
            if len(prev_points) > 0 and len(next_points) > 0:
                prev = prev_points.iloc[-1]
                next_pt = next_points.iloc[0]
                time_delta = (next_pt['timestamp'] - prev['timestamp']).total_seconds()
                position_ratio = (idx - prev.name) / (next_pt.name - prev.name) if next_pt.name != prev.name else 0.5
                new_timestamp = prev['timestamp'] + timedelta(seconds=time_delta * position_ratio)
                df.at[idx, 'timestamp'] = new_timestamp
        except Exception as e:
            print(f"  警告: 为掩码点 {idx} 分配时间戳时出错: {e}")
            continue

    if 'timestamp' in df.columns:
        valid_timestamps = df.dropna(subset=['timestamp'])
        if not valid_timestamps.empty:
            try:
                df = df.sort_values('timestamp')
            except Exception as e:
                print(f"  警告: 按时间戳排序时出错: {e}")

    # 清洗数据
    try:
        cleaned_df = clean_gps_data(df)
        # 添加速度、方向和曲率特征
        cleaned_df = calculate_trajectory_features(cleaned_df)
        return cleaned_df
    except Exception as e:
        print(f"  警告: 清洗数据时出错: {e}")
        return df

def generate_train_samples(df, mask_ratio=0.2):
    samples = []
    if len(df) < 3:
        return samples

    mask_indices = np.random.choice(range(1, len(df) - 1), size=max(1, int(len(df) * mask_ratio)), replace=False)
    for idx in mask_indices:
        prev = df.iloc[idx - 1]
        next_pt = df.iloc[idx + 1]
        current = df.iloc[idx]

        if pd.isna(prev['timestamp']) or pd.isna(current['timestamp']) or pd.isna(next_pt['timestamp']):
            continue
        if pd.isna(prev['lon']) or pd.isna(prev['lat']) or pd.isna(next_pt['lon']) or pd.isna(next_pt['lat']):
            continue
        if pd.isna(current['lon']) or pd.isna(current['lat']):
            continue

        delta_prev = (current['timestamp'] - prev['timestamp']).total_seconds()
        delta_next = (next_pt['timestamp'] - current['timestamp']).total_seconds()
        if delta_prev <= 0 or delta_next <= 0:
            continue

        total_delta = delta_prev + delta_next
        rel_time = delta_prev / total_delta if total_delta != 0 else 0

        features = {
            'prev_lon': prev['lon'],
            'prev_lat': prev['lat'],
            'next_lon': next_pt['lon'],
            'next_lat': next_pt['lat'],
            'rel_time': rel_time,
            'total_delta': total_delta,
            'prev_speed': prev['speed'],
            'prev_direction': prev['direction'],
            'prev_curvature': prev['curvature'],
            'next_speed': next_pt['speed'],
            'next_direction': next_pt['direction'],
            'next_curvature': next_pt['curvature']
        }
        target = {'target_lon': current['lon'], 'target_lat': current['lat']}
        samples.append({**features, **target})

    return samples

def calculate_average_metrics(pred_trajectories, true_trajectories):
    mse_list = []
    frechet_list = []
    for pred_traj, true_traj in zip(pred_trajectories, true_trajectories):
        if len(pred_traj) == 0 or len(true_traj) == 0:
            continue
        pred_array = np.array(pred_traj)
        true_array = np.array(true_traj)
        try:
            if not np.isnan(pred_array).any() and not np.isnan(true_array).any():
                mse = mean_squared_error(true_array, pred_array)
                if mse > 1e-10:
                    mse_list.append(mse)
        except Exception as e:
            print(f"计算MSE时出错: {e}")
        try:
            if len(pred_traj) > 1 and len(true_traj) > 1:
                if not np.isnan(pred_array).any() and not np.isnan(true_array).any():
                    frechet = similaritymeasures.frechet_dist(true_array, pred_array)
                    if frechet > 1e-10:
                        frechet_list.append(frechet)
        except Exception as e:
            print(f"计算Frechet距离时出错: {e}")
    
    metrics_stats = {
        'mse': {
            'count': len(mse_list),
            'mean': np.mean(mse_list) if mse_list else np.nan,
            'median': np.median(mse_list) if mse_list else np.nan,
            'std': np.std(mse_list) if mse_list else np.nan,
            'min': np.min(mse_list) if mse_list else np.nan,
            'max': np.max(mse_list) if mse_list else np.nan
        },
        'frechet': {
            'count': len(frechet_list),
            'mean': np.mean(frechet_list) if frechet_list else np.nan,
            'median': np.median(frechet_list) if frechet_list else np.nan,
            'std': np.std(frechet_list) if frechet_list else np.nan,
            'min': np.min(frechet_list) if frechet_list else np.nan,
            'max': np.max(frechet_list) if frechet_list else np.nan
        }
    }
    
    avg_mse = metrics_stats['mse']['mean']
    avg_frechet = metrics_stats['frechet']['mean']
    
    return avg_mse, avg_frechet, metrics_stats

def print_metrics_summary(metrics_stats):
    print("\n=== MSE统计 ===")
    print(f"样本数: {metrics_stats['mse']['count']}")
    print(f"平均值: {metrics_stats['mse']['mean']:.6f}")
    print(f"中位数: {metrics_stats['mse']['median']:.6f}")
    print(f"标准差: {metrics_stats['mse']['std']:.6f}")
    print(f"最小值: {metrics_stats['mse']['min']:.6f}")
    print(f"最大值: {metrics_stats['mse']['max']:.6f}")
    
    print("\n=== Frechet距离统计 ===")
    print(f"样本数: {metrics_stats['frechet']['count']}")
    print(f"平均值: {metrics_stats['frechet']['mean']:.6f}")
    print(f"中位数: {metrics_stats['frechet']['median']:.6f}")
    print(f"标准差: {metrics_stats['frechet']['std']:.6f}")
    print(f"最小值: {metrics_stats['frechet']['min']:.6f}")
    print(f"最大值: {metrics_stats['frechet']['max']:.6f}")

def calculate_all_metrics(pred_coords, true_coords):
    metrics = {}
    try:
        metrics['mse'] = mean_squared_error(true_coords, pred_coords)
        metrics['rmse'] = math.sqrt(metrics['mse'])
        metrics['mae'] = mean_absolute_error(true_coords, pred_coords)
        metrics['frechet'] = similaritymeasures.frechet_dist(true_coords, pred_coords)
        distance, _ = fastdtw(true_coords, pred_coords, dist=euclidean)
        metrics['dtw'] = distance
        return metrics
    except Exception as e:
        print(f"计算指标时出错: {e}")
        return None
    
def save_metrics_to_file(metrics_list, output_file):
    """
    将评估指标保存到文本文件
    """
    try:
        with open(output_file, 'w') as f:
            f.write("轨迹评估指标统计\n")
            f.write("=" * 50 + "\n\n")
            
            # 计算每个指标的统计值
            stats = {
                'mse': [], 'rmse': [], 'mae': [], 
                'frechet': [], 'dtw': []
            }
            
            for metrics in metrics_list:
                for key in stats.keys():
                    if key in metrics:
                        stats[key].append(metrics[key])
            
            # 写入统计结果
            for metric_name in stats:
                if stats[metric_name]:
                    values = np.array(stats[metric_name])
                    f.write(f"\n{metric_name.upper()} 统计:\n") 
                    f.write(f"样本数: {len(values)}\n")
                    f.write(f"平均值: {np.mean(values):.6f}\n")
                    f.write(f"中位数: {np.median(values):.6f}\n")
                    f.write(f"标准差: {np.std(values):.6f}\n")
                    f.write(f"最小值: {np.min(values):.6f}\n")
                    f.write(f"最大值: {np.max(values):.6f}\n")
                    f.write("-" * 30 + "\n")
    except Exception as e:
        print(f"保存指标到文件时出错: {e}")
        print(f"保存指标到文件时出错: {e}")

def visualize_metrics(metrics_list, output_dir):
    """可视化评估指标，生成箱线图和直方图"""
    try:
        stats = {
            'mse': [], 'rmse': [], 'mae': [], 
            'frechet': [], 'dtw': []
        }
        for metrics in metrics_list:
            for key in stats.keys():
                if key in metrics and isinstance(metrics[key], (int, float)) and not np.isnan(metrics[key]):
                    stats[key].append(metrics[key])

        # 检查是否有有效数据
        valid_metrics = [key for key, values in stats.items() if values]
        if not valid_metrics:
            print("警告: 没有有效的评估指标数据，无法生成可视化")
            return

        # 箱线图
        plt.figure(figsize=(15, 6))
        plt.boxplot(
            [stats[key] for key in valid_metrics],
            labels=[key.upper() for key in valid_metrics]
        )
        plt.title('轨迹预测误差指标分布')
        plt.ylabel('误差值')
        plt.xticks(rotation=45)
        plt.tight_layout()
        boxplot_path = os.path.join(output_dir, 'metrics_boxplot.png')
        plt.savefig(boxplot_path)
        plt.close()
        print(f"箱线图已保存到: {boxplot_path}")

        # 直方图
        for metric_name in valid_metrics:
            plt.figure(figsize=(8, 6))
            plt.hist(stats[metric_name], bins=30, edgecolor='black')
            plt.title(f'{metric_name.upper()} 分布')
            plt.xlabel('误差值')
            plt.ylabel('频次')
            hist_path = os.path.join(output_dir, f'{metric_name}_histogram.png')
            plt.savefig(hist_path)
            plt.close()
            print(f"{metric_name.upper()} 直方图已保存到: {hist_path}")
    except Exception as e:
        print(f"可视化指标时出错: {e}")

def predict_and_evaluate(input_dir, true_dir, model, output_dir=None, evaluate=True, is_test=False, scaler=None):
    print(f'开始处理文件夹: {input_dir}')
    all_metrics_list = []
    file_count = 0
    predicted_mask_points = 0
    total_mask_points = 0

    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    metrics_dir = os.path.join(output_dir, 'metrics') if output_dir else None
    if metrics_dir:
        os.makedirs(metrics_dir, exist_ok=True)

    test_file_dir = None
    if is_test:
        test_file_dir = 'test_file'
        if not os.path.exists(test_file_dir):
            os.makedirs(test_file_dir)

    if not os.path.exists(input_dir):
        print(f"错误: 输入目录 {input_dir} 不存在")
        return None, None

    input_files = os.listdir(input_dir)
    if not input_files:
        print(f"警告: 输入目录 {input_dir} 为空")
        return None, None

    for masked_file in input_files:
        file_count += 1
        print(f'处理文件 ({file_count}/{len(input_files)}): {masked_file}')
        masked_path = os.path.join(input_dir, masked_file)
        if not os.path.isfile(masked_path) or not masked_file.endswith('.txt'):
            print(f"  警告: {masked_file} 不是有效的文本文件，跳过")
            continue

        true_path = os.path.join(true_dir, masked_file) if true_dir and os.path.exists(
            os.path.join(true_dir, masked_file)) else None

        if evaluate and true_path is None:
            print(f"  警告: 找不到对应的真实轨迹文件 {masked_file}，跳过评估")
            if output_dir:
                true_path = None
            else:
                continue

        masked_df = parse_trajectory(masked_path)
        if masked_df.empty:
            print(f"  错误: 无法解析掩码轨迹文件 {masked_file}，跳过该文件")
            continue

        true_df = None
        if true_path and evaluate:
            true_df = parse_trajectory(true_path)
            if true_df.empty:
                print(f"  警告: 无法解析真实轨迹文件 {masked_file}，将无法评估")

        repaired_df = masked_df.copy()
        predictions_made = 0
        file_mask_points = 0

        if 'mask' not in masked_df.columns:
            print(f"  错误: 数据中没有mask列，跳过该文件")
            continue

        mask_points_count = masked_df['mask'].sum()
        if mask_points_count == 0:
            print(f"  警告: 文件 {masked_file} 中没有掩码点，跳过预测")
            continue

        total_mask_points += mask_points_count
        valid_points = {}
        for idx, row in masked_df.iterrows():
            if not row['mask'] and not pd.isna(row['lon']) and not pd.isna(row['lat']):
                valid_points[idx] = (row['timestamp'], row['lon'], row['lat'], row['speed'], row['direction'], row['curvature'])

        valid_indices = sorted(valid_points.keys())
        for idx, row in masked_df.iterrows():
            if row['mask']:
                file_mask_points += 1
                try:
                    prev_points = masked_df.iloc[:idx][~masked_df.iloc[:idx]['mask']]
                    next_points = masked_df.iloc[idx + 1:][~masked_df.iloc[idx + 1:]['mask']]

                    if len(prev_points) == 0 or len(next_points) == 0:
                        print(f"  警告: 掩码点 {idx} 没有足够的前后非掩码点，使用线性插值")
                        if len(valid_indices) >= 2:
                            closest_before = None
                            closest_after = None
                            for valid_idx in valid_indices:
                                if valid_idx < idx and (closest_before is None or valid_idx > closest_before):
                                    closest_before = valid_idx
                                if valid_idx > idx and (closest_after is None or valid_idx < closest_after):
                                    closest_after = valid_idx
                            if closest_before is None and closest_after is not None:
                                closest_before = valid_indices[0]
                            if closest_after is None and closest_before is not None:
                                closest_after = valid_indices[-1]
                            if closest_before is not None and closest_after is not None:
                                before_time, before_lon, before_lat, _, _, _ = valid_points[closest_before]
                                after_time, after_lon, after_lat, _, _, _ = valid_points[closest_after]
                                if row['timestamp'] is not None:
                                    time_ratio = ((row['timestamp'] - before_time).total_seconds() /
                                                  (after_time - before_time).total_seconds())
                                    time_ratio = max(0, min(1, time_ratio))
                                else:
                                    time_ratio = 0.5
                                interpolated_lon = before_lon + (after_lon - before_lon) * time_ratio
                                interpolated_lat = before_lat + (after_lat - before_lat) * time_ratio
                                repaired_df.at[idx, 'lon'] = interpolated_lon
                                repaired_df.at[idx, 'lat'] = interpolated_lat
                                predictions_made += 1
                                continue
                            else:
                                if len(valid_indices) > 0:
                                    nearest_idx = valid_indices[0]
                                    _, nearest_lon, nearest_lat, _, _, _ = valid_points[nearest_idx]
                                    repaired_df.at[idx, 'lon'] = nearest_lon
                                    repaired_df.at[idx, 'lat'] = nearest_lat
                                    predictions_made += 1
                                    continue
                                else:
                                    repaired_df.at[idx, 'lon'] = 116.0
                                    repaired_df.at[idx, 'lat'] = 40.0
                                    predictions_made += 1
                                    continue
                        else:
                            repaired_df.at[idx, 'lon'] = 116.0
                            repaired_df.at[idx, 'lat'] = 40.0
                            predictions_made += 1
                            continue

                    prev = prev_points.iloc[-1]
                    next_pt = next_points.iloc[0]

                    if (pd.isna(prev['lon']) or pd.isna(prev['lat']) or
                        pd.isna(next_pt['lon']) or pd.isna(next_pt['lat'])):
                        print(f"  警告: 掩码点 {idx} 的相关坐标数据无效，使用时间线性插值")
                        if not pd.isna(prev['lon']) and not pd.isna(prev['lat']):
                            repaired_df.at[idx, 'lon'] = prev['lon']
                            repaired_df.at[idx, 'lat'] = prev['lat']
                        elif not pd.isna(next_pt['lon']) and not pd.isna(next_pt['lat']):
                            repaired_df.at[idx, 'lon'] = next_pt['lon']
                            repaired_df.at[idx, 'lat'] = next_pt['lat']
                        else:
                            repaired_df.at[idx, 'lon'] = 116.0
                            repaired_df.at[idx, 'lat'] = 40.0
                        predictions_made += 1
                        continue

                    if pd.isna(row['timestamp']) or pd.isna(prev['timestamp']) or pd.isna(next_pt['timestamp']):
                        print(f"  警告: 掩码点 {idx} 的时间戳数据无效，使用空间线性插值")
                        repaired_df.at[idx, 'lon'] = (prev['lon'] + next_pt['lon']) / 2
                        repaired_df.at[idx, 'lat'] = (prev['lat'] + next_pt['lat']) / 2
                        predictions_made += 1
                        continue

                    delta_prev = (row['timestamp'] - prev['timestamp']).total_seconds()
                    delta_next = (next_pt['timestamp'] - row['timestamp']).total_seconds()
                    if delta_prev <= 0 or delta_next <= 0:
                        print(f"  警告: 掩码点 {idx} 的时间差异不正确，使用空间线性插值")
                        repaired_df.at[idx, 'lon'] = (prev['lon'] + next_pt['lon']) / 2
                        repaired_df.at[idx, 'lat'] = (prev['lat'] + next_pt['lat']) / 2
                        predictions_made += 1
                        continue

                    total_delta = delta_prev + delta_next
                    rel_time = delta_prev / total_delta if total_delta != 0 else 0

                    features = pd.DataFrame([{
                        'prev_lon': prev['lon'],
                        'prev_lat': prev['lat'],
                        'next_lon': next_pt['lon'],
                        'next_lat': next_pt['lat'],
                        'rel_time': rel_time,
                        'total_delta': total_delta,
                        'prev_speed': prev['speed'],
                        'prev_direction': prev['direction'],
                        'prev_curvature': prev['curvature'],
                        'next_speed': next_pt['speed'],
                        'next_direction': next_pt['direction'],
                        'next_curvature': next_pt['curvature']
                    }])

                    # 特征标准化
                    if scaler is not None:
                        features_scaled = scaler.transform(features)
                        features = pd.DataFrame(features_scaled, columns=features.columns)

                    pred = model.predict(features)
                    repaired_df.at[idx, 'lon'] = pred[0][0]
                    repaired_df.at[idx, 'lat'] = pred[0][1]
                    predictions_made += 1
                except Exception as e:
                    print(f"  警告: 预测掩码点 {idx} 时出错: {e}，使用默认值")
                    if len(valid_indices) >= 2:
                        first_idx = valid_indices[0]
                        last_idx = valid_indices[-1]
                        _, first_lon, first_lat, _, _, _ = valid_points[first_idx]
                        _, last_lon, last_lat, _, _, _ = valid_points[last_idx]
                        pos_ratio = 0.5
                        if first_idx != last_idx:
                            pos_ratio = (idx - first_idx) / (last_idx - first_idx)
                            pos_ratio = max(0, min(1, pos_ratio))
                        interpolated_lon = first_lon + (last_lon - first_lon) * pos_ratio
                        interpolated_lat = first_lat + (last_lat - first_lat) * pos_ratio
                        repaired_df.at[idx, 'lon'] = interpolated_lon
                        repaired_df.at[idx, 'lat'] = interpolated_lat
                    else:
                        repaired_df.at[idx, 'lon'] = 116.0
                        repaired_df.at[idx, 'lat'] = 40.0
                    predictions_made += 1
                    continue

        predicted_mask_points += predictions_made
        print(f'  已修复 {predictions_made}/{file_mask_points} 个掩码点')

        if output_dir:
            output_path = os.path.join(output_dir, masked_file)
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    for idx, row in repaired_df.iterrows():
                        if pd.isna(row['timestamp']):
                            continue
                        if not row['mask']:
                            f.write(f"{row['timestamp'].strftime('%Y-%m-%d %H:%M:%S')},{row['lon']},{row['lat']}\n")
                        else:
                            if not pd.isna(row['lon']) and not pd.isna(row['lat']):
                                f.write(f"{row['timestamp'].strftime('%Y-%m-%d %H:%M:%S')},{row['lon']},{row['lat']}\n")
                print(f'  预测结果已保存到: {output_path}')
            except Exception as e:
                print(f"  错误: 保存预测结果时出错: {e}")

        if is_test and test_file_dir:
            try:
                mask_line_numbers = get_mask_positions(masked_path)
                if mask_line_numbers:
                    valid_mask_indices = masked_df[masked_df['line_num'].isin(mask_line_numbers)].index.tolist()
                    if not valid_mask_indices:
                        print(f"  警告: 原始文件MASK行号 {mask_line_numbers} 未在DataFrame中找到对应记录")
                        continue
                    valid_mask_indices.sort()
                    first_mask_idx = valid_mask_indices[0]
                    last_mask_idx = valid_mask_indices[-1]
                    prev_point_idx = first_mask_idx - 1 if first_mask_idx != 0 else None
                    start_idx = prev_point_idx if prev_point_idx is not None else first_mask_idx
                    next_point_idx = None
                    for i in range(last_mask_idx + 1, len(masked_df)):
                        if not masked_df.iloc[i]['mask']:
                            next_point_idx = i
                            break
                    end_idx = next_point_idx if next_point_idx is not None else last_mask_idx
                    output_segment = repaired_df.iloc[start_idx:end_idx + 1].copy()
                    test_file_path = os.path.join(test_file_dir, masked_file)
                    with open(test_file_path, 'w', encoding='utf-8') as f:
                        for _, row in output_segment.iterrows():
                            if pd.isna(row['timestamp']):
                                continue
                            if not pd.isna(row['lon']) and not pd.isna(row['lat']):
                                f.write(f"{row['timestamp'].strftime('%Y-%m-%d %H:%M:%S')},{row['lon']},{row['lat']}\n")
                    print(f'  测试文件结果已保存到: {test_file_path}')
                else:
                    print(f"  警告: 在文件 {masked_file} 中没有找到掩码点")
            except Exception as e:
                print(f"  错误: 保存测试文件结果时出错: {e}")

        if true_df is not None and evaluate and predictions_made > 0:
            try:
                original_mask_points = masked_df[masked_df['mask']]
                if len(original_mask_points) > 0:
                    mask_line_nums = original_mask_points['line_num'].tolist()
                    valid_repaired = repaired_df.dropna(subset=['lon', 'lat'])
                    pred_points = []
                    true_points = []
                    for line_num in mask_line_nums:
                        pred_point = valid_repaired[valid_repaired['line_num'] == line_num]
                        true_point = true_df[true_df['line_num'] == line_num]
                        if (not pred_point.empty and not true_point.empty and 
                            not pd.isna(pred_point['lon'].values[0]) and 
                            not pd.isna(pred_point['lat'].values[0]) and
                            not pd.isna(true_point['lon'].values[0]) and  
                            not pd.isna(true_point['lat'].values[0])):
                            pred_points.append([pred_point['lon'].values[0], pred_point['lat'].values[0]])
                            true_points.append([true_point['lon'].values[0], true_point['lat'].values[0]])
                    if len(pred_points) > 0:
                        pred_coords = np.array(pred_points)
                        true_coords = np.array(true_points)
                        if not np.isnan(pred_coords).any() and not np.isnan(true_coords).any():
                            metrics = calculate_all_metrics(pred_coords, true_coords)
                            if metrics:
                                metrics['file_name'] = masked_file
                                metrics['points_count'] = len(pred_points)
                                all_metrics_list.append(metrics)
                                print(f"\n文件 {masked_file} 的评估指标:")
                                for metric_name, value in metrics.items():
                                    if isinstance(value, (int, float)):
                                        print(f"  {metric_name}: {value:.6f}")
            except Exception as e:
                print(f"  警告: 评估轨迹时出错: {e}")

        if output_dir:
            try:
                output_path = os.path.join(output_dir, masked_file)
                with open(output_path, 'w', encoding='utf-8') as f:
                    for idx, row in repaired_df.iterrows():
                        if pd.isna(row['timestamp']):
                            continue
                        if not row['mask'] or not pd.isna(row['lon']) and not pd.isna(row['lat']):
                            f.write(f"{row['timestamp'].strftime('%Y-%m-%d %H:%M:%S')},{row['lon']},{row['lat']}\n")
                print(f'  预测结果已保存到: {output_path}')
            except Exception as e:
                print(f"  错误: 保存预测结果时出错: {e}")

    if evaluate and len(all_metrics_list) > 0:
        try:
            if metrics_dir:
                metrics_file = os.path.join(metrics_dir, 'evaluation_metrics.txt')
                save_metrics_to_file(all_metrics_list, metrics_file)
                visualize_metrics(all_metrics_list, metrics_dir)
                print(f"\n评估指标已保存到 {metrics_dir} 目录")
            avg_metrics = {
                'mse': np.mean([m['mse'] for m in all_metrics_list]),
                'frechet': np.mean([m['frechet'] for m in all_metrics_list])
            }
            return avg_metrics['mse'], avg_metrics['frechet']
        except Exception as e:
            print(f"警告: 保存评估结果时出错: {e}")
            return np.nan, np.nan

    return None, None

