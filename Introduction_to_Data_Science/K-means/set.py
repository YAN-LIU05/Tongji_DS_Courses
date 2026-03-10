import numpy as np
import csv

# 数据集的参数
n_samples = 300  # 数据点总数
n_features = 2  # 特征数（二维数据）
n_clusters = 4  # 聚类簇的数量
random_state = 15  # 随机种子，用于结果可复现
cluster_std = 1.9  # 每个簇的标准差（控制数据点分布的紧密程度）

# 设置随机种子以确保每次生成的数据集一致
np.random.seed(random_state)

# 随机生成聚类簇的中心点
centers = np.random.uniform(-10, 10, (n_clusters, n_features))  # 在[-10, 10]范围内生成簇中心

# 根据簇中心生成数据点，数据点围绕中心随机分布
X = []  # 初始化数据集列表
for center in centers:
    # 在每个中心点周围生成 n_samples // n_clusters 个数据点
    X.append(center + cluster_std * np.random.randn(n_samples // n_clusters, n_features))
X = np.vstack(X)  # 将数据点堆叠为二维数组

# 将数据集保存到 CSV 文件中
data_filename = "dataset.csv"  # 文件名
with open(data_filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Feature1", "Feature2"])  # 写入表头
    writer.writerows(X)  # 写入数据点

print(f"包含 {n_samples} 个样本和 {n_features} 个特征的数据集已保存到 '{data_filename}'")  # 打印提示信息
