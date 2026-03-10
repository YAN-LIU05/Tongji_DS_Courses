clear all; clc; close all;

% 参数
x0 = 0; % 初始点
y0 = 1; % y(0) = 1
dy0 = 0; % y'(0) = 0
h = 0.05; % 步长
x_end = 2; % 终止点

% 定义 x 范围（用于数值解）
x_rk4 = x0:h:x_end;
N = length(x_rk4);

% 初始化解向量
Y_rk4 = zeros(2, N);
Y_rk4(:, 1) = [y0; dy0]; % 初始条件 [y, y']

% 定义方程组
f = @(x, Y) [Y(2); -Y(1)*cos(x)];

% 四阶龙格-库塔方法 (RK4)
for i = 1:N-1
    k1 = h * f(x_rk4(i), Y_rk4(:, i));
    k2 = h * f(x_rk4(i) + h/2, Y_rk4(:, i) + k1/2);
    k3 = h * f(x_rk4(i) + h/2, Y_rk4(:, i) + k2/2);
    k4 = h * f(x_rk4(i) + h, Y_rk4(:, i) + k3);
    Y_rk4(:, i+1) = Y_rk4(:, i) + (k1 + 2*k2 + 2*k3 + k4)/6;
end

% 级数解：从 x = 0 到 x = 2
x_series = 0:0.01:2; % 级数解的 x 范围
y_series = 1 - (1/factorial(2)) * x_series.^2 + (2/factorial(4)) * x_series.^4 - ...
           (9/factorial(6)) * x_series.^6 + (55/factorial(8)) * x_series.^8;

% 绘制对比图
figure;
plot(x_series, y_series, 'b-', 'LineWidth', 1, 'DisplayName', '级数解'); % 级数解
hold on;
plot(x_rk4, Y_rk4(1, :), 'r*', 'MarkerSize', 5, 'DisplayName', '数值解 (RK4)'); % 数值解
xlabel('$x$', 'Interpreter', 'latex');
ylabel('$y$', 'Interpreter', 'latex', 'Rotation', 0);
title('级数解和数值解对比 (RK4)', 'Interpreter', 'latex');
legend('Location', 'northeast');
grid on;
