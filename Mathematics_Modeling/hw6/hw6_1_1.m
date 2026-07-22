clc; clear; close all;

% 读取数据
filename = 'hw6_1.txt';
opts = detectImportOptions(filename, 'Delimiter', '\t'); % 假设用制表符分隔
T = readtable(filename, opts);

% 提取变量
province = T{:, 1}; % 第一列是省份名称
X = table2array(T(:, 2:end)); % 数值部分
X_norm = zscore(X); % 标准化数值数据

% 层次聚类
z = linkage(X_norm, 'single'); % 使用单连接法

% 绘制树状图
figure;
dendrogram(z, 0, 'Labels', province, 'Orientation', 'left'); % 0 表示显示所有节点
title('层次聚类树状图');

% 自动选择最优 k（基于轮廓系数）
max_k = 10;
silhouette_avg = zeros(1, max_k);
for k = 1:max_k
    idx = cluster(z, 'maxclust', k); % 切割聚类树
    sil = silhouette(X_norm, idx, 'euclidean'); % 计算轮廓系数
    silhouette_avg(k) = mean(sil); % 平均轮廓系数
end
[~, optimal_k] = max(silhouette_avg);
fprintf('基于轮廓系数的最优 k: %d\n', optimal_k);

% 绘制轮廓系数图
figure;
plot(1:max_k, silhouette_avg, '-o');
xlabel('聚类数 k');
ylabel('平均轮廓系数');
title('轮廓系数确定最优聚类数');

% 使用最优 k 执行聚类并输出结果
idx = cluster(z, 'maxclust', optimal_k);
for i = 1:optimal_k
    fprintf('聚类 %d:\n', i);
    disp(province(idx == i)); % 显示每个簇的标签
end

% PCA 可视化
[coeff, score] = pca(X_norm);
figure;
gscatter(score(:,1), score(:,2), idx);
xlabel('PCA 1'); ylabel('PCA 2');
title('城市结构特征聚类可视化');
text(score(:,1)+0.02, score(:,2), province, 'FontSize', 8);