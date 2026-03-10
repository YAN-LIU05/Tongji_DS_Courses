import os
import pandas as pd
import numpy as np
from datetime import datetime

input_dir = r"test_file"

def smooth_coordinates(file_path):
    # 读取文件并解析
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split(',')
            if len(parts) == 3:
                timestamp = parts[0]
                lon = float(parts[1])
                lat = float(parts[2])
                data.append([timestamp, lon, lat])

    df = pd.DataFrame(data)

    # 处理经度(第1列)和纬度(第2列)
    for col in [1, 2]:
        # 获取值变化的位置
        changes = df[col].ne(df[col].shift())

        # 找出连续相同值的段落
        start_idx = 0
        for i in range(1, len(df)):
            if changes.iloc[i] or i == len(df) - 1:
                end_idx = i
                # 如果段落中有3个及以上相同值
                if end_idx - start_idx > 2:
                    start_val = df[col].iloc[start_idx]
                    end_val = df[col].iloc[end_idx]

                    # 计算均匀递增/递减的值
                    num_points = end_idx - start_idx + 1
                    if start_val != end_val:
                        values = np.linspace(start_val, end_val, num_points)
                        df.loc[start_idx:end_idx, col] = values

                start_idx = i

    # 保存修改后的文件
    output_dir = input_dir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, os.path.basename(file_path))

    # 保持原有格式写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        for i in range(len(df)):
            f.write(f"{df.iloc[i, 0]},{df.iloc[i, 1]:.12g},{df.iloc[i, 2]:.12g}\n")

    return output_path


def process_all_files():

    # 获取目录下所有 txt 文件
    files = [f for f in os.listdir(input_dir) if f.endswith('.txt')]

    for file in files:
        print(f"处理文件: {file}")
        try:
            file_path = os.path.join(input_dir, file)
            output_path = smooth_coordinates(file_path)
            print(f"处理完成，保存到: {output_path}")
        except Exception as e:
            print(f"处理文件 {file} 时出错: {e}")



def read_trajectory_file(file_path):
    """读取轨迹文件并返回字典，以时间戳为键"""
    data_dict = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) == 3:
                    timestamp = parts[0]
                    data_dict[timestamp] = (parts[1], parts[2])
    except Exception as e:
        print(f"读取文件 {file_path} 时出错: {e}")
    return data_dict


def process_files(folder1, folder2):
    """处理两个文件夹中的文件"""
    # 确保输出目录存在
    output_dir = os.path.join(folder1, 'replaced')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 获取第一个文件夹中的所有txt文件
    files = [f for f in os.listdir(folder1) if f.endswith('.txt')]

    for file_name in files:
        print(f"处理文件: {file_name}")

        # 构建文件路径
        file1_path = os.path.join(folder1, file_name)
        file2_path = os.path.join(folder2, file_name)

        # 检查第二个文件夹中是否存在同名文件
        if not os.path.exists(file2_path):
            print(f"在第二个文件夹中未找到对应文件: {file_name}")
            continue

        try:
            # 读取两个文件
            data1 = []  # 保存原始文件的所有行
            data2_dict = read_trajectory_file(file2_path)  # 第二个文件的数据字典

            # 处理第一个文件
            with open(file1_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split(',')
                    if len(parts) == 3:
                        timestamp = parts[0]
                        # 如果时间戳在第二个文件中存在，使用第二个文件的值
                        if timestamp in data2_dict:
                            lon, lat = data2_dict[timestamp]
                            data1.append(f"{timestamp},{lon},{lat}")
                        else:
                            data1.append(line.strip())

            # 保存处理后的文件
            output_path = os.path.join(output_dir, file_name)
            with open(output_path, 'w', encoding='utf-8') as f:
                for line in data1:
                    f.write(line + '\n')

            print(f"文件处理完成: {file_name}")

        except Exception as e:
            print(f"处理文件 {file_name} 时出错: {e}")


import shutil

def final_deal():
    # 指定两个文件夹
    folder1 = input_dir
    folder2 = r"test_masked"
    replaced_folder = os.path.join(folder1, 'replaced')

    if not os.path.exists(folder1) or not os.path.exists(folder2):
        print("错误：文件夹路径不存在")
        return

    # 处理文件，生成 replaced 文件夹
    process_files(folder1, folder2)

    # 删除 folder1 中的所有 .txt 文件（除了 replaced 文件夹内的）
    for f in os.listdir(folder1):
        file_path = os.path.join(folder1, f)
        if f.endswith('.txt') and os.path.isfile(file_path):
            os.remove(file_path)
            print(f"已删除: {file_path}")

    # 移动 replaced 文件夹中的 .txt 文件回 folder1
    if os.path.exists(replaced_folder):
        for f in os.listdir(replaced_folder):
            src_path = os.path.join(replaced_folder, f)
            dst_path = os.path.join(folder1, f)
            if f.endswith('.txt') and os.path.isfile(src_path):
                shutil.move(src_path, dst_path)
                print(f"已移动: {src_path} → {dst_path}")

        # 删除 replaced 文件夹
        shutil.rmtree(replaced_folder)
        print(f"已删除 replaced 文件夹: {replaced_folder}")

    print("所有文件处理完成")


final_deal()
process_all_files()





