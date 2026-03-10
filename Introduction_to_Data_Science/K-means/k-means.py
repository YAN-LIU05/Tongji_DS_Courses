import numpy as np
import matplotlib.pyplot as plt
import csv

# 第一步：从 CSV 文件中加载数据集
data_filename = "dataset.csv"  # 数据文件名
X = []
with open(data_filename, mode='r') as file:
    reader = csv.reader(file)
    next(reader)  # 跳过表头
    for row in reader:
        X.append([float(value) for value in row])  # 将每一行数据转换为浮点数并添加到列表中
X = np.array(X)  # 将列表转换为 NumPy 数组

print(f"读入数据库：{data_filename}中的数据")  # 打印提示信息

# 第二步：定义自定义的 K-Means 聚类算法
class KMeansCustom:
    def __init__(self, n_clusters, max_iter=300, tol=1e-4):
        """
        初始化 K-Means 模型
        :param n_clusters: 聚类簇数
        :param max_iter: 最大迭代次数
        :param tol: 收敛容忍度
        """
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self.tol = tol

    def fit(self, X):
        """
        训练模型
        :param X: 输入数据集 (二维数组)
        """
        n_samples, n_features = X.shape
        # 随机初始化质心
        random_idx = np.random.permutation(n_samples)[:self.n_clusters]
        self.centroids = X[random_idx]

        for i in range(self.max_iter):
            # 分配每个点到最近的质心
            self.labels = self._assign_clusters(X)

            # 可视化当前迭代的聚类结果
            self._plot_iteration(X, i)

            # 更新质心
            new_centroids = self._update_centroids(X)

            # 检查是否收敛
            if np.linalg.norm(self.centroids - new_centroids, axis=None) < self.tol:
                break
            self.centroids = new_centroids

    def _assign_clusters(self, X):
        """
        计算每个点到质心的距离并分配到最近的质心
        :param X: 输入数据集
        :return: 每个点对应的簇标签
        """
        distances = np.linalg.norm(X[:, np.newaxis] - self.centroids, axis=2)
        return np.argmin(distances, axis=1)

    def _update_centroids(self, X):
        """
        更新每个簇的质心为簇内所有点的均值
        :param X: 输入数据集
        :return: 更新后的质心
        """
        centroids = np.zeros((self.n_clusters, X.shape[1]))
        for k in range(self.n_clusters):
            points = X[self.labels == k]  # 获取属于簇 k 的所有点
            if len(points) > 0:
                centroids[k] = points.mean(axis=0)  # 计算均值
        return centroids

    def _plot_iteration(self, X, iteration):
        """
        绘制每次迭代的聚类过程
        :param X: 输入数据集
        :param iteration: 当前迭代次数
        """
        plt.figure(figsize=(8, 6))
        plt.scatter(X[:, 0], X[:, 1], c=self.labels, s=50, cmap='viridis', label='Data Points')
        plt.scatter(self.centroids[:, 0], self.centroids[:, 1], c='red', s=200, alpha=0.75, label='Centroids')
        plt.title(f"Iteration {iteration + 1}")
        plt.xlabel("Feature x")
        plt.ylabel("Feature y")
        plt.legend()
        plt.grid(True)
        plt.show()

    def predict(self, X):
        """
        根据模型预测数据的簇标签
        :param X: 输入数据集
        :return: 每个点对应的簇标签
        """
        return self._assign_clusters(X)

# 第三步：应用自定义的 K-Means 聚类算法
n_clusters = 4  # 聚类簇数
kmeans = KMeansCustom(n_clusters=n_clusters)
kmeans.fit(X)  # 训练模型
y_kmeans = kmeans.predict(X)  # 获取聚类结果

# 第四步：最终聚类结果的可视化
plt.figure(figsize=(8, 6))

# 绘制数据点，用簇标签的颜色区分
plt.scatter(X[:, 0], X[:, 1], c=y_kmeans, s=50, cmap='viridis', label='Data Points')

# 绘制质心
centers = kmeans.centroids
plt.scatter(centers[:, 0], centers[:, 1], c='red', s=200, alpha=0.75, label='Centroids')

plt.title("K-Means Clustering Results")
plt.xlabel("Feature x")
plt.ylabel("Feature y")
plt.legend()
plt.grid(True)
plt.show()
