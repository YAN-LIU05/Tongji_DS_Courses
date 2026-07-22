% MATLAB 代码：使用 ode45 求解 y'' + y*cos(x) = 0 的数值解，级数解从 x = 0 开始，数值解从初始点之后绘制
clear all;
clc;
close all;

% 参数
x0 = 0; % 初始点
y0 = 1; % y(0) = 1
dy0 = 0; % y'(0) = 0
xspan = [0, 2]; % 求解区间 [0, 2]

% 定义方程组
dy = @(x, y) [y(2); -y(1)*cos(x)];

% 使用 ode45 求解数值解
[x_ode45, y_ode45] = ode45(dy, xspan, [y0; dy0]);

% 级数解：从 x = 0 到 x = 2
x_series = 0:0.01:2; % 级数解的 x 范围
y_series = 1 - (1/factorial(2)) * x_series.^2 + (2/factorial(4)) * x_series.^4 - ...
           (9/factorial(6)) * x_series.^6 + (55/factorial(8)) * x_series.^8;

% 绘制对比图
figure;
plot(x_series, y_series, 'b-', 'LineWidth', 1, 'DisplayName', '级数解'); % 级数解
hold on;
plot(x_ode45, y_ode45(:, 1), 'r*', 'MarkerSize', 5, 'DisplayName', '数值解 (ode45)'); % 数值解
xlabel('$x$', 'Interpreter', 'latex');
ylabel('$y$', 'Interpreter', 'latex', 'Rotation', 0);
title('级数解和数值解对比 (ode45)', 'Interpreter', 'latex');
legend('Location', 'northeast');
grid on;

% 保存图形（可选）
% print('-dpng', 'series_ode45_comparison.png');