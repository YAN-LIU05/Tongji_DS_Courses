clc; clear; format long g;

% 定义参数
profit = [3100; 3800; 3500; 2850]; % 利润系数
max_weight = [18; 15; 23; 12]; % 货物重量上限
hold_weight = [10; 16; 8]; % 货舱重量上限
hold_volume = [6800; 8700; 5300]; % 货舱体积上限
cargo_volume = [480; 650; 580; 390]; % 货物空间需求 (m³/t)

% 目标函数系数 (转换为最小化问题)
f = -repmat(profit, 3, 1); % 复制利润向量，使其匹配变量数

% 不等式约束
A = [
    repmat(eye(4), 1, 3);      % 每种货物的最大装载量
    kron(eye(3), ones(1, 4));  % 货舱重量限制
    kron(eye(3), cargo_volume');          % 货舱体积限制
];
b = [
    max_weight; % 货物重量限制
    hold_weight; % 货舱重量限制
    hold_volume; % 货舱体积限制
];

% 等式约束：货舱载重量成比例
Aeq = zeros(2, 12); % 初始化等式约束矩阵
Aeq(1, 1:4) = 1 / hold_weight(1); % 前舱总载重量 / w1
Aeq(1, 5:8) = -1 / hold_weight(2); % 中舱总载重量 / w2
Aeq(2, 5:8) = 1 / hold_weight(2); % 中舱总载重量 / w2
Aeq(2, 9:12) = -1 / hold_weight(3); % 后舱总载重量 / w3
beq = zeros(2, 1); % 等式约束的右侧为0

% 变量上下界
lb = zeros(12,1);    % 变量下界

% 求解线性规划
options = optimoptions('linprog', 'Display', 'off');
[x, fval, exitflag] = linprog(f, A, b, Aeq, beq, lb, [], options);

% 结果处理
if exitflag == 1
    max_profit = -fval;
    x_ij = reshape(x, 4, 3); % 重塑解向量为 4×3 矩阵
    
    % 显示结果
    fprintf('最大利润为：%.4E 元\n', max_profit);
    fprintf('各货舱装载量（吨）：\n');
    fprintf('前舱：%.4f 吨\n', sum(x_ij(:,1)));
    fprintf('中舱：%.4f 吨\n', sum(x_ij(:,2)));
    fprintf('后舱：%.4f 吨\n', sum(x_ij(:,3)));
    
    % 各货物分配详情
    cargo_names = {'货物1', '货物2', '货物3', '货物4'};
    disp('货物分配（吨）：');
    for i = 1:4
        fprintf('%s:\n', cargo_names{i});
        fprintf('  前舱: %.4f 吨\n', x_ij(i,1));
        fprintf('  中舱: %.4f 吨\n', x_ij(i,2));
        fprintf('  后舱: %.4f 吨\n', x_ij(i,3));
    end
else
    error('未找到可行解。');
end