clc; clear; close all;

% 1. 读取数据
T = readtable('hw6_2.txt');
year = T{:,1};
X = T{:,2:end};

% 2. 数据标准化
Z = zscore(X);  

% ========== 特征值 + 特征向量分析 ==========
R = corrcoef(Z);                         % 相关系数矩阵
[eigVec, eigVal_matrix] = eig(R);        % 特征值分解
eigVal = diag(eigVal_matrix);            % 提取特征值
[eigVal_sorted, idx] = sort(eigVal, 'descend');  
eigVec_sorted = eigVec(:, idx);          % 排序后的特征向量（按特征值顺序）

% 计算贡献率
total = sum(eigVal_sorted);
contribution_rate = eigVal_sorted / total;
cumulative_rate = cumsum(contribution_rate);

% 输出前5个特征值及贡献率
fprintf('前5个特征值及其贡献率：\n');
fprintf('----------------------------------------------\n');
fprintf('主成分\t特征值\t\t贡献率(%%)\t累计贡献率(%%)\n');
for i = 1:5
    fprintf('PC%d\t\t%.4f\t\t%.2f%%\t\t%.2f%%\n', ...
        i, eigVal_sorted(i), contribution_rate(i)*100, cumulative_rate(i)*100);
end
fprintf('----------------------------------------------\n\n');

% ========== 输出前3个主成分对应的特征向量 ==========
fprintf('前3个主成分的特征向量（对应标准化变量系数）：\n');
for i = 1:3
    fprintf('y%d = ', i);
    for j = 1:size(eigVec_sorted,1)
        coef = eigVec_sorted(j,i);
        if coef >= 0 && j > 1
            fprintf('+ ');
        end
        fprintf('%.4f * x%d ', coef, j);
    end
    fprintf('\n');
end
fprintf('\n');

% ========== 主成分分析 ==========
[coeff, score, latent, ~, explained] = pca(Z);  % explained为每个主成分贡献率（%）

% ========== 综合得分计算 ==========
explained_ratio = explained / 100;
composite_score = score * explained_ratio;

% ========== 综合得分排序 ==========
[sorted_score, idx] = sort(composite_score, 'descend');
sorted_year = year(idx);

% 输出结果
disp('年份排序结果（按投资效益）：');
disp(table(sorted_year, sorted_score));

% ========== 全部主成分综合评价模型 ==========
figure;
bar(score(:,1), 'FaceColor', [0.2 0.6 0.8]);
xticks(1:length(year)); xticklabels(string(year)); xtickangle(45);
ylabel('第一主成分得分');
title('第一主成分得分（代表主要投资效益）'); grid on;

figure;
bar(composite_score, 'FaceColor', [0.4 0.7 0.2]);
xticks(1:length(year)); xticklabels(string(year)); xtickangle(45);
ylabel('综合得分');
title('各年份投资效益综合得分（主成分加权）'); grid on;

% ========== 前3主成分综合评价模型 ==========
score_3 = score(:,1:3);                  % 取前3个主成分得分
weight_3 = explained(1:3);               % 前3主成分贡献率（百分比）
weight_3 = weight_3 / sum(weight_3);     % 转为归一化权重
score_3_weighted = score_3 * weight_3;   % 前3主成分加权得分

% 排序并输出
[sorted_score3, idx3] = sort(score_3_weighted, 'descend');
sorted_year3 = year(idx3);
fprintf('\n根据前三主成分构建的综合评价模型结果：\n');
disp(table(sorted_year3, sorted_score3));

% 可视化
figure;
bar(score_3_weighted, 'FaceColor', [0.7 0.4 0.4]);
xticks(1:length(year)); xticklabels(string(year)); xtickangle(45);
ylabel('前3主成分加权得分');
title('投资效益综合评价（基于前3个主成分）'); grid on;
