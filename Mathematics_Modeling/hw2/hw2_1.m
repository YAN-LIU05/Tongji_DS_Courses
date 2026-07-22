clc; clear;

% 交货需求
delivery = [40; 60; 80]; % 每季度的交货量
production_capacity = 100; % 每季度的最大生产能力
storage_cost_per_unit = 4; % 每台发动机每季度的存储费用
production_cost_coefficients = [50, 0.2]; % 生产费用系数 [线性项, 二次项]

% **计算存储成本的固定部分**
% 假设每季度生产量分别为 x1, x2, x3：
% 存储量计算公式：库存 = 生产 - 交货（累积计算）
storage_cost_fixed = sum(storage_cost_per_unit * cumsum(delivery)); 

% **二次规划参数**
H = diag(2 * production_cost_coefficients(2) * ones(3, 1)); % 二次项系数矩阵
f = production_cost_coefficients(1) + storage_cost_per_unit * [3; 2; 1]; % 线性项系数

% **约束条件**
A = [-1  0  0;            % x1 ≥ 40
     -1 -1  0;            % x1 + x2 ≥ 100
     -1 -1 -1;            % x1 + x2 + x3 ≥ 180
      1  0  0;            % x1 ≤ 100
      0  1  0;            % x2 ≤ 100
      0  0  1];           % x3 ≤ 100
b = [-40; -100; -180; 100; 100; 100];

% 变量上下界
lb = zeros(3, 1); % 生产量下限
ub = production_capacity * ones(3, 1); % 生产量上限

% **求解二次规划问题**
[x_opt, fval] = quadprog(H, f, A, b, [], [], lb, ub);

% **计算总费用**
total_cost = fval - storage_cost_fixed;

% **显示结果**
disp('各季度最优生产量：');
disp(['x1 = ', num2str(x_opt(1)), ' 件']);
disp(['x2 = ', num2str(x_opt(2)), ' 件']);
disp(['x3 = ', num2str(x_opt(3)), ' 件']);
disp(['计算得出存储费用固定部分：', num2str(storage_cost_fixed), ' 元']);
disp(['总费用：', num2str(total_cost), ' 元']);
