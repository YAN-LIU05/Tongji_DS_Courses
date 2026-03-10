clc, clear

% 样本数据
x0 = [1050 1100 1120 1250 1280]';

% 样本数量
n = length(x0);
fprintf('样本数量 n: %d\n', n);

% 置信水平
alpha = 0.10; % 1 - 0.90
fprintf('置信水平 alpha: %.2f\n', alpha);

% 计算 t 分布临界值
Ta = tinv(1 - alpha/2, n-1); % t 分布临界值，自由度为 n-1
fprintf('t 分布临界值 Ta: %.4f\n', Ta);

% 拟合正态分布
pd = fitdist(x0, 'Normal'); % 拟合正态分布
fprintf('拟合正态分布的均值 mu: %.2f\n', pd.mu);
fprintf('拟合正态分布的标准差 sigma: %.4f\n', pd.sigma);

% 使用 paramci 计算置信区间（参考值）
ci = paramci(pd, 'Alpha', alpha); % 计算正态分布均值的置信区间
fprintf('置信水平为 0.90 的置信区间: [%.1f, %.1f]\n', ci(1,1), ci(2,1));

% 手动计算置信区间，与 paramci 匹配
mean_x = pd.mu; % 使用 fitdist 的均值
s = pd.sigma; % 使用 fitdist 的标准差
SE = s / sqrt(n); % 标准误差
margin_error = Ta * SE; % 误差范围
ci_manual_lower = mean_x - margin_error; % 下限
ci_manual_upper = mean_x + margin_error; % 上限
fprintf('手动计算的置信区间: [%.1f, %.1f]\n', ci_manual_lower, ci_manual_upper);

% 生成正态分布曲线
x = linspace(min(x0)-100, max(x0)+100, 100);
y = normpdf(x, pd.mu, pd.sigma);
plot(x, y, 'r-', 'LineWidth', 2);

% 添加标题和标签
title('正态分布拟合');
xlabel('寿命 (小时)');
ylabel('概率密度');
legend('拟合的正态分布曲线');
grid on;