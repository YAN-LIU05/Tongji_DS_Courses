clc, clear

% 样本数据
x0 = [15.0 15.8 15.2 15.1 15.9 14.7 14.8 15.5 15.6 15.3 ...
      15.1 15.3 15.0 15.6 15.7 14.8 14.5 14.2 14.9 14.9 ...
      15.2 15.0 15.3 15.6 15.1 14.9 14.2 14.6 15.8 15.2 ...
      15.9 15.2 15.0 14.9 14.8 14.5 15.1 15.5 15.5 15.1 ...
      15.1 15.0 15.3 14.7 14.5 15.5 15.0 14.7 14.6 14.2]';

% 样本数量
n = length(x0);
fprintf('样本数量 n: %d\n', n);

% 样本均值和标准差
mean_x = mean(x0);
s = std(x0, 1);
fprintf('样本均值 x̄: %.4f\n', mean_x);
fprintf('样本标准差 s: %.4f\n', s);

% 分组区间
intervals = [-Inf, 14.71, 14.88, 15.05, 15.22, 15.39, 15.56, Inf];

% 计算频数
observed_freq = zeros(1, length(intervals)-1);
for i = 1:length(intervals)-1
    if i == 1
        observed_freq(i) = sum(x0 <= intervals(i+1));
    elseif i == length(intervals)-1
        observed_freq(i) = sum(x0 > intervals(i));
    else
        observed_freq(i) = sum(x0 > intervals(i) & x0 <= intervals(i+1));
    end
end

% 理论概率
theoretical_prob = [0.1974, 0.1261, 0.1506, 0.1545, 0.1360, 0.1028, 0.1325];
theoretical_freq = n * theoretical_prob;

% 卡方检验
chi2_stat = sum((observed_freq - theoretical_freq).^2 ./ theoretical_freq);
fprintf('卡方统计量 χ²: %.4f\n', chi2_stat);

% 卡方临界值
df = length(observed_freq) - 2 - 1;
chi2_crit = chi2inv(0.95, df);
fprintf('自由度 df: %d\n', df);
fprintf('卡方临界值 χ²(0.05, %d): %.4f\n', df, chi2_crit);

% 检验结论
if chi2_stat < chi2_crit
    fprintf('χ² < 临界值，无法拒绝原假设，数据服从 N(15.0780, 0.4325^2)。\n');
else
    fprintf('χ² ≥ 临界值，拒绝原假设，数据不服从 N(15.0780, 0.4325^2)。\n');
end

% 置信区间
alpha = 0.05;
Za = norminv(1 - alpha/2);
fprintf('\n置信区间计算：\n');
fprintf('正态分布临界值 Za: %.4f\n', Za);

SE = s / sqrt(n);
margin_error = Za * SE;
ci_lower = mean_x - margin_error;
ci_upper = mean_x + margin_error;
fprintf('置信水平为 0.95 的置信区间: [%.4f, %.4f]\n', ci_lower, ci_upper);

% 验证规格
spec_mean = 15.0780;
spec_std = 0.4325;
if ci_lower <= spec_mean && ci_upper >= spec_mean
    fprintf('置信区间包含规格均值 %.4f，均值符合规格。\n', spec_mean);
else
    fprintf('置信区间不包含规格均值 %.4f，均值不符合规格。\n', spec_mean);
end
if abs(s - spec_std) < 1e-4
    fprintf('样本标准差 %.4f 与规格标准差 %.4f 一致，标准差符合规格。\n', s, spec_std);
end

% 绘图
pd = fitdist(x0, 'Normal');
x = linspace(min(x0)-1, max(x0)+1, 100);
y = normpdf(x, pd.mu, pd.sigma);
plot(x, y, 'r-', 'LineWidth', 2);
title('正态分布拟合');
xlabel('直径 (mm)');
ylabel('概率密度');
legend('拟合的正态分布曲线');
grid on;