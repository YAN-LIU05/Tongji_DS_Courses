clear all; clc; close all;

% 参数
n = 1/2; % 贝塞尔方程参数
x0 = pi/2; % 初始点
y0 = 2; % y(pi/2) = 2
dy0 = -2/pi; % y'(pi/2) = -2/pi
h = 0.1; % 步长
x_start = 0.001; % 解析解起始点（避免 x = 0）
x_end = 8; % 终止点

% --- 解析解 ---
x_analytical = x_start:h:x_end;
y_analytical = sqrt(2*pi./x_analytical) .* sin(x_analytical);

% --- 数值解 ---
x_numerical = x0:h:x_end;
N_numerical = length(x_numerical);
Y_numerical = zeros(2, N_numerical);
Y_numerical(:, 1) = [y0; dy0]; % 初始条件

% 定义方程组
f = @(x, Y) [Y(2); -(x*Y(2) + (x^2 - n^2)*Y(1))/x^2];

% RK4 方法（从 x = pi/2 向右）
for i = 1:N_numerical-1
    k1 = h * f(x_numerical(i), Y_numerical(:, i));
    k2 = h * f(x_numerical(i) + h/2, Y_numerical(:, i) + k1/2);
    k3 = h * f(x_numerical(i) + h/2, Y_numerical(:, i) + k2/2);
    k4 = h * f(x_numerical(i) + h, Y_numerical(:, i) + k3);
    Y_numerical(:, i+1) = Y_numerical(:, i) + (k1 + 2*k2 + 2*k3 + k4)/6;
end

% 绘制对比图
figure;
plot(x_analytical, y_analytical, 'b-', 'LineWidth', 1, 'DisplayName', '解析解'); % 解析解
hold on;
plot(x_numerical, Y_numerical(1, :), 'r*', 'MarkerSize', 5, 'DisplayName', '数值解 (RK4)'); % 数值解
xlabel('$x$', 'Interpreter', 'latex');
ylabel('$y$', 'Interpreter', 'latex', 'Rotation', 0);
title('符号解和数值解对比 (RK4)', 'Interpreter', 'latex');
legend('Location', 'northeast');
grid on;
