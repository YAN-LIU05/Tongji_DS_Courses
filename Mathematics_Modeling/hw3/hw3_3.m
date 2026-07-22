clc; clear; close all;
% 读取数据
a = load('hw3_3.txt');
t0 = a(:, [1,3]); t0 = t0(:);
h0 = a(:, [2,4]); h0 = h0(:);

% 确保时间序列单调递增
[t0, sort_idx] = sort(t0);
h0 = h0(sort_idx);

% 处理 -1（泵水过程）: 插值填充缺失的水位
missing_idx = (h0 == -1);
h0(missing_idx) = interp1(t0(~missing_idx), h0(~missing_idx), t0(missing_idx), 'pchip');

% 计算水箱体积
E = 0.3024; % 1E = 30.24 cm
D = 57 * E; % 直径
t = t0/3600; % 时间转换为小时
V = pi * (D^2) .* (h0/100 * E)/4;  % 水箱体积 (cm³)

% 计算水流速 f(t)（数值导数）
dV_dt = diff(V) ./ diff(t); % 差分法计算流速
t_mid = t(2:end);  % 让 t_mid 和 dV_dt 长度一致

% 对流速进行插值
t_interp = linspace(min(t_mid), max(t_mid), 500);
f_interp = interp1(t_mid, dV_dt, t_interp, 'pchip'); % 使用三次样条插值

% 绘制流速曲线
figure;
plot(t_mid, dV_dt, 'ro', 'MarkerFaceColor', 'r'); hold on;
plot(t_interp, f_interp, 'b-', 'LineWidth', 1.5);
xlabel('时间 (小时)'); ylabel('流速 f(t) (cm³/小时)');
title('水箱流速曲线');
legend('原始数据', '插值曲线');
grid on;

% 计算总用水量
% 1. 非泵水阶段的流出量 (f_interp < 0)
outflow_non_pumping_idx = f_interp < 0;
f_outflow_non_pumping = -f_interp .* outflow_non_pumping_idx; % 负值转为正值，表示流出

% 2. 估算泵水阶段的流出率 (假设与非泵水阶段平均流出率相同)
avg_outflow_rate = mean(f_outflow_non_pumping(outflow_non_pumping_idx)); % 非泵水阶段平均流出率
pumping_idx = f_interp > 0;
f_outflow_pumping = avg_outflow_rate * ones(size(f_interp)) .* pumping_idx; % 泵水阶段假设恒定流出率

% 3. 总流出量 = 非泵水阶段流出 + 泵水阶段流出
f_outflow_total = f_outflow_non_pumping + f_outflow_pumping;

% 4. 平滑流出曲线
cs = csape(t_interp, f_outflow_total, [1 1], [0 0]); % 端点一阶导数为 0
f_outflow_smooth = ppval(cs, t_interp); % 计算平滑后的值
f_outflow_smooth = max(f_outflow_smooth, 0);
f_outflow_smooth = smooth(f_outflow_smooth, 30, 'moving'); % 窗口大小 10，增强平滑

% 5. 数值积分计算总用水量（使用平滑后的曲线）
total_water = trapz(t_interp, f_outflow_smooth);

% 输出结果
fprintf('24 小时总用水量: %.2f 立方厘米\n', total_water);

% 可视化流出量
figure;
plot(t_interp, f_outflow_smooth, 'g-', 'LineWidth', 1.5);
xlabel('时间 (小时)'); ylabel('流出流速 (cm³/小时)');
title('水箱总流出流速曲线');
legend('流出曲线');
grid on;