% 目标函数（取负以实现最大化）
fun = @(x) -(2*x(1) + 3*x(1)^2 + 3*x(2) + x(2)^2 + x(3));

% 线性不等式约束 A*x ≤ b
A = [-1, -2, 0];
b = -1;

% 变量下界
lb = [0; -inf; -inf];

% 初始点1：x1=0, x2=0.5, x3=2
x0_1 = [0; 0.5; 2];
options = optimoptions('fmincon', 'Display', 'off', 'Algorithm', 'sqp');
[x1, fval1] = fmincon(fun, x0_1, A, b, [], [], lb, [], @nonlcon, options);

% 初始点2：x1=1, x2=0, x3=1
x0_2 = [1; 0; 1];
[x2, fval2] = fmincon(fun, x0_2, A, b, [], [], lb, [], @nonlcon, options);

% 选择更优解
if -fval1 > -fval2
    x_opt = x1;
    f_opt = -fval1;
else
    x_opt = x2;
    f_opt = -fval2;
end

% 显示结果
disp('最优解:');
disp(['x1 = ', num2str(x_opt(1))]);
disp(['x2 = ', num2str(x_opt(2))]);
disp(['x3 = ', num2str(x_opt(3))]);
disp(['目标函数最大值: ', num2str(f_opt)]);

% 非线性约束函数
function [c, ceq] = nonlcon(x)
    c = [x(1) + 2*x(1)^2 + x(2) + 2*x(2)^2 + x(3) - 10;
         x(1) + x(1)^2 + x(2) + x(2)^2 - x(3) - 50;
         2*x(1) + x(1)^2 + 2*x(2) + x(3) - 40];
    ceq = x(1)^2 + x(3) - 2;
end