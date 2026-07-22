clc; clear; close all;

% 定义优化目标函数
objFun = @(x) sum(x.^2);

% 设定初始值和约束
x0 = rand(6,1);
lb = -30 * ones(6,1);
ub = 30 * ones(6,1);

% 调用 fmincon 进行优化
[xOpt, objVal] = fmincon(objFun, x0, [], [], [], [], lb, ub, @conFun);

% 输出结果
disp('Optimal solution:');
disp(xOpt);
disp('Objective function value:');
disp(objVal);

% ---- 局部函数 ----
function [ineq, eq] = conFun(x)
    % 定义非线性不等式约束的函数
    eq = []; % 不存在非线性等式约束
    th0 = [243 236 220.5 159 230 52]'; % 初始角度
    th = th0 + x;                      % 调整后角度
    xPos = [150 85 150 145 130 0]';   % x 坐标
    yPos = [140 85 155 50 150 0]';    % y 坐标
    min_distance = 8;                 % 最小不碰撞距离
    
    % 计算不等式约束
    ineq = zeros(15,1); % 预分配约束数组
    k = 1;              % 约束索引
    for i = 1:5
        for j = i + 1:6
            a = 4 * (sind((th(i) - th(j)) / 2))^2;
            b = 2 * ((xPos(i) - xPos(j)) * (cosd(th(i)) - cosd(th(j))) + ...
                     (yPos(i) - yPos(j)) * (sind(th(i)) - sind(th(j))));
            c = (xPos(i) - xPos(j))^2 + (yPos(i) - yPos(j))^2 - min_distance^2;
            ineq(k) = b^2 - 4 * a * c;
            k = k + 1;
        end
    end
end