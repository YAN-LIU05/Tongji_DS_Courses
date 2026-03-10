clc; clear; close all;

% 定义优化目标函数
objFun = @(t) sum(t.^2);

% 初始值和边界
t0 = rand(6,1);
lb = -30 * ones(6,1);
ub = 30 * ones(6,1);


% 罚函数法参数
M = 100000;      % 初始罚因子
tol = 1e-6;     % 收敛容差
t = t0;         % 初始解

% 迭代求解
for k = 1:15
    % 定义带罚项的目标函数
    penalizedObj = @(t) objFun(t) + M * sum(max(0, conFun(t)).^2);
    
    % 使用无约束优化（fminunc）求解
    options = optimoptions('fminunc', 'Display', 'off');
    [tNew, fVal] = fminunc(@(t) boundPenalty(t, penalizedObj, lb, ub), t, options);
    
    % 检查约束违反程度
    ineq = conFun(tNew);
    violation = sum(max(0, ineq));
    
    % 判断是否收敛
    if violation < tol
        break;
    end
    
    % 更新解和罚因子
    t = tNew;
    M = M * 10; % 增大罚因子
end

% 输出结果
disp('Optimal solution:');
disp(t);
disp('Objective function value:');
disp(objFun(t));
disp('Constraint violation:');
disp(sum(max(0, conFun(t))));

% ---- 局部函数：约束函数 ----
function g = conFun(t)
    th0 = [243 236 220.5 159 230 52]'; % 初始角度
    th = th0 + t;                      % 调整后角度
    x0 = [150 85 150 145 130 0]';     % x 坐标
    y0 = [140 85 155 50 150 0]';      % y 坐标
    min_distance = 8;                 % 最小不碰撞距离
    
    g = zeros(15,1); % 预分配约束数组
    k = 1;
    for i = 1:5
        for j = i + 1:6
            a = 4 * (sind((th(i) - th(j)) / 2))^2;
            b = 2 * ((x0(i) - x0(j)) * (cosd(th(i)) - cosd(th(j))) + ...
                     (y0(i) - y0(j)) * (sind(th(i)) - sind(th(j))));
            c = (x0(i) - x0(j))^2 + (y0(i) - y0(j))^2 - min_distance^2;
            g(k) = b^2 - 4 * a * c;
            k = k + 1;
        end
    end
end

% ---- 局部函数：处理边界约束的罚函数 ----
function f = boundPenalty(t, penalizedObj, lb, ub)
    penalty = 1e6 * (sum(max(0, lb - t).^2) + sum(max(0, t - ub).^2));
    f = penalizedObj(t) + penalty;
end