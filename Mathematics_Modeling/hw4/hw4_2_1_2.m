% MATLAB 代码：使用 ode45 求解贝塞尔方程的数值解，解析解从 x = 0 开始，数值解从初始点之后绘制
clear all;
clc;
close all;

% 参数
n = 1/2;
x0 = pi/2; % 初始点
y0 = 2; % y(pi/2) = 2
dy0 = -2/pi; % y'(pi/2) = -2/pi
xspan = [pi/2, 8]; % 求解区间 [pi/2, 8]

% 定义方程组
dy = @(x, y) [y(2); -(x*y(2) + (x^2 - n^2)*y(1))/x^2];

% 使用 ode45 求解数值解
[x_ode45, y_ode45] = ode45(dy, xspan, [y0; dy0]);

% 解析解：从 x = 0.001 到 x = 8
x_analytical = 0.001:0.01:8; % 解析解的 x 范围
y_exact_analytical = sqrt(2*pi./x_analytical) .* sin(x_analytical);

% 绘制对比图
figure;
plot(x_analytical, y_exact_analytical, 'b-', 'LineWidth', 1, 'DisplayName', '解析解'); % 解析解
hold on;
plot(x_ode45, y_ode45(:, 1), 'r*', 'MarkerSize', 5, 'DisplayName', '数值解 (ode45)'); % 数值解
xlabel('$x$', 'Interpreter', 'latex');
ylabel('$y$', 'Interpreter', 'latex', 'Rotation', 0);
title('符号解和数值解对比 (ode45)', 'Interpreter', 'latex');
legend('Location', 'northeast');
grid on;

% 保存图形（可选）
% print('-dpng', 'bessel_comparison_ode45_from_zero.png');