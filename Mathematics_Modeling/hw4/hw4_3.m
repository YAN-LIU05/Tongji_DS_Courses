clc, clear

% 参数
d = 100; % 河宽 (m)
v1 = 1; % 小船在静水中的速度 (m/s)
v2 = 2; % 河水流速 (m/s)
k = v1 / v2; % k = v1 / v2

% 定义微分方程
dxy = @(t, xy) [-v2 * xy(1) / sqrt(xy(1)^2 + xy(2)^2); ...
                v1 - v2 * xy(2) / sqrt(xy(1)^2 + xy(2)^2)];

% 初始条件
xy0 = [d; 0]; % x(0) = d, y(0) = 0

% 求解微分方程
[t, xy] = ode45(dxy, [0, 69], xy0);

% 找到渡河时间
t_cross = 0;
for i = 1:length(t)
    if xy(i, 1) <= 0.01 % 当 x 小于 0.01 时，认为到达 B 点
        t_cross = t(i);
        break;
    end
end

fprintf('数值解渡河时间 t = %.2f 秒\n', t_cross);

% 解析解轨迹
x_analytical = linspace(0, d, 100); % x 从 0 到 d
y_analytical = (1/2) * (d^k * x_analytical.^(1-k) - x_analytical.^(1+k) / d^k);
% 避免 x = 0 时的奇异点
y_analytical(x_analytical == 0) = 0;

% 绘制轨迹对比图
figure;
plot(xy(:, 1), xy(:, 2), 'b-', 'LineWidth', 2, 'DisplayName', '数值解');
hold on;
plot(x_analytical, y_analytical, 'r*', 'MarkerSize', 5, 'DisplayName', '解析解');
xlabel('x (m)');
ylabel('y (m)');
title('数值解与解析解轨迹对比');
legend;
grid on;


% 解析解渡河时间（数值积分）
f = @(x) (1/2) * sqrt(0.0025 * x.^3 + 25 * x + 0.5 * x.^2) ./ x;
t_analytical = integral(f, 0, 100, 'RelTol', 1e-6, 'AbsTol', 1e-6);
fprintf('解析解渡河时间（数值积分） t = %.2f 秒\n', t_analytical);


