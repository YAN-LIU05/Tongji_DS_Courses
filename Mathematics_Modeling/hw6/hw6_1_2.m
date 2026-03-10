filename = 'hw6_1.txt';

% 假设文件是以空格或制表符分隔
opts = detectImportOptions(filename, 'Delimiter', '\t');  % 或 ' ' 空格
T = readtable(filename, opts);

% 提取变量
province = T{:, 1};  % 第一列是省份名称
X = table2array(T(:, 2:end));  % 数值部分
X_norm = zscore(X);

sumd_all = zeros(1, 10);
for k = 1:10
    [~, ~, sumd] = kmeans(X_norm, k, 'Replicates', 10);
    sumd_all(k) = sum(sumd);
end

figure;
plot(1:10, sumd_all, '-o');
xlabel('聚类数 k');
ylabel('总距离（SSE）');
title('肘部法确定最优聚类数');

% 选择 k
diff1 = diff(sumd_all); % 一阶差分（斜率）
diff2 = diff(diff1);    % 二阶差分（斜率的变化）
[~, max_change_idx] = max(abs(diff2)); % 找到二阶差分绝对值最大的点
optimal_k = max_change_idx + 2; % 加 2 因为 diff2 比 sumd_all 短两个元素

fprintf('选择的最优 k: %d\n', optimal_k);

[idx, C] = kmeans(X_norm, optimal_k, 'Replicates', 10);

for i = 1:optimal_k
    fprintf('聚类 %d:\n', i);
    disp(province(idx == i));
end

[coeff, score] = pca(X_norm);

figure;
gscatter(score(:,1), score(:,2), idx);
xlabel('PCA 1'); ylabel('PCA 2');
title('城市结构特征聚类可视化');
text(score(:,1)+0.02, score(:,2), province, 'FontSize', 8);

