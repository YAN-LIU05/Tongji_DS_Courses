% 步骤 1：输入数据
x = [1, 2, 3, 4, 5, 6, 7, 8]; % x_i 数据
y = [15.3, 20.5, 27.4, 36.6, 49.1, 65.6, 87.8, 117.6]; % y_i 数据

% 步骤 2：线性化处理
Y = log(y); % 取 y 的自然对数

% 步骤 3：用最小二乘法拟合线性模型 Y = A + bx
% 构造设计矩阵（线性模型）
n = length(x);
X = [ones(n, 1), x']; % 设计矩阵 [1, x]
coeff = (X' * X) \ (X' * Y'); % 最小二乘解：(X'X)^(-1) * X'Y
A = coeff(1); % 截距 A
b = coeff(2); % 斜率 b
a = exp(A); % a = e^A

% 步骤 4：输出拟合结果
fprintf('线性化最小二乘法拟合结果：\n');
fprintf('a = %.4f, b = %.4f\n', a, b);

% 步骤 5：计算误差（平方和）
y_pred = a * exp(b * x); % 预测值
error = sum((y - y_pred).^2); % 误差平方和
fprintf('误差平方和：%.4f\n', error);

% 步骤 6：生成拟合曲线
x_fit = linspace(min(x), max(x), 100); % 生成平滑的 x 值用于绘图
y_fit = a * exp(b * x_fit); % 计算拟合的 y 值

% 步骤 7：绘制数据点和拟合曲线
figure;
plot(x, y, 'ro', 'MarkerSize', 8, 'LineWidth', 1.5); % 绘制原始数据点
hold on;
plot(x_fit, y_fit, 'b-', 'LineWidth', 2); % 绘制拟合曲线
grid on;
xlabel('x');
ylabel('y');
title('线性化最小二乘法拟合：y = ae^{bx}');
legend('数据点', sprintf('拟合曲线 y = %.4fe^{%.4fx}', a, b));
hold off;