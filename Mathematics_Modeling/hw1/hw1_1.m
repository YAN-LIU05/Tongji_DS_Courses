clc; clear; format short g;

% 定义10个整数决策变量
x_I_A1  = optimvar('x_I_A1',  'Type', 'integer', 'LowerBound', 0);
x_I_A2  = optimvar('x_I_A2',  'Type', 'integer', 'LowerBound', 0);
x_I_B1  = optimvar('x_I_B1',  'Type', 'integer', 'LowerBound', 0);
x_I_B2  = optimvar('x_I_B2',  'Type', 'integer', 'LowerBound', 0);
x_I_B3  = optimvar('x_I_B3',  'Type', 'integer', 'LowerBound', 0);
x_II_A1  = optimvar('x_II_A1',  'Type', 'integer', 'LowerBound', 0);
x_II_A2  = optimvar('x_II_A2',  'Type', 'integer', 'LowerBound', 0);
x_II_B1  = optimvar('x_II_B1',  'Type', 'integer', 'LowerBound', 0);
x_III_A2  = optimvar('x_III_A2',  'Type', 'integer', 'LowerBound', 0);
x_III_B2 = optimvar('x_III_B2', 'Type', 'integer', 'LowerBound', 0);

% 定义优化问题，最大化目标函数
optProblem = optimproblem('ObjectiveSense', 'max');

% 目标函数
optProblem.Objective = x_I_A1 + x_I_A2 + 1.65 * x_II_B1 + 2.3 * x_III_A2 - 0.05 * (5 * x_I_A1 + 10 * x_II_A1) ...
    - 0.0321 * (7 * x_I_A2 + 9 * x_II_A2 + 12 * x_III_A2) - 0.0625 * (6 * x_I_B1 + 8 * x_II_B1) ...
    - (783 / 7000) * (4 * x_I_B2 + 11 * x_III_B2) - 0.35 * x_I_B3;

% 约束条件
optProblem.Constraints.resourceLimits = [
    5 * x_I_A1 + 10 * x_II_A1 <= 6000;
    7 * x_I_A2 + 9 * x_II_A2 + 12 * x_III_A2 <= 10000;
    6 * x_I_B1 + 8 * x_II_B1 <= 4000;
    4 * x_I_B2 + 11 * x_III_B2 <= 7000;
    7 * x_I_B3 <= 4000
];

% 生产平衡约束
optProblem.Constraints.balance = [
    x_I_A1 + x_I_A2 == x_I_B1 + x_I_B2 + x_I_B3;
    x_II_A1 + x_II_A2 == x_II_B1;
    x_III_A2 == x_III_B2
];

% 求解问题
[solution, optimalValue, exitFlag] = solve(optProblem);

% 输出结果
disp('最优解:');
disp(solution);
disp(['最大化目标值: ', num2str(optimalValue)]);
