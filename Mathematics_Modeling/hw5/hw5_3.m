clc; clear;

data = [
    98 93 103 92 110;
    100 108 118 99 111;
    129 140 108 105 116
];

% 将数据展开为一列（15个观测值）
Y = data';       % 先转置变成 5行3列（每列是一个组）
Y = Y(:);        % 变成15×1的列向量

% 构造对应的组标签
group = [repmat({'组1'}, 5, 1); repmat({'组2'}, 5, 1); repmat({'组3'}, 5, 1)];

% 单因素方差分析
[p, t, st] = anova1(Y, group);

% 提取F值
F_value = cell2mat(t(2, 5));  % 第2行第5列是F值

% 输出结果
disp("F = " + F_value);

% F分布临界值
F_critical = finv(1 - 0.05, 2, 12);
if F_value > F_critical
    fprintf('F值%.4f超过临界值%.4f，拒绝原假设，表明三组数据的均值存在显著差异 \n', F_value, F_critical);
else
    fprintf('F值%.4f未超过临界值%.4f，无法拒绝原假设，表明三组数据的均值不存在显著差异 \n', F_value, F_critical); 
end
