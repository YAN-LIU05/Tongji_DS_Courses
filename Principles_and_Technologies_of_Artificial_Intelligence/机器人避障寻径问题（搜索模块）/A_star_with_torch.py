# 2352018 刘彦
import numpy as np
import heapq
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time
import torch
import torch.nn as nn
import torch.optim as optim
from tqdm import tqdm

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'KaiTi', 'FangSong']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False     # 用来正常显示负号

# 定义场景图（题设要求）
grid = np.loadtxt("grid_preset.txt", dtype=int)

# 设置起点和终点
start = (2, 3) 
end = (3, 7) 

# 定义场景图（20x20网格，1为障碍物，0为可通行区域）
# grid = np.loadtxt("grid_new.txt", dtype=int)

# # 修改起点和终点位置
# start = (0, 0)      # 左上角
# end = (19, 19)      # 右下角

# 定义神经网络模型（优化：更轻量，添加Dropout）
class HeuristicNet(nn.Module):
    def __init__(self):
        super(HeuristicNet, self).__init__()
        self.fc1 = nn.Linear(4, 32)  # 输入：4个特征（x, y, 邻域比例，曼哈顿距离）
        self.fc2 = nn.Linear(32, 1)  # 输出：预测距离
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.3)

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x

# 生成训练数据：为每个可通行节点计算到终点的真实距离
def generate_training_data(grid, end):
    rows, cols = grid.shape
    X = []
    y = []
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def get_neighbors_feature(node):
        # 计算 5x5 邻域的障碍物比例（更广范围）
        x, y = node
        count = 0
        total = 0
        for dx in [-2, -1, 0, 1, 2]:
            for dy in [-2, -1, 0, 1, 2]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < rows and 0 <= ny < cols:
                    count += grid[nx, ny]
                    total += 1
        return count / total if total > 0 else 0

    def astar_distance(start, end):
        distances = {start: 0}
        pq = [(0, start)]
        visited = set()

        while pq:
            dist, current = heapq.heappop(pq)
            if current in visited:
                continue
            visited.add(current)
            if current == end:
                return dist

            for dx, dy in directions:
                nx, ny = current[0] + dx, current[1] + dy
                if (0 <= nx < rows and 0 <= ny < cols and
                        grid[nx, ny] == 0 and (nx, ny) not in visited):
                    new_dist = dist + 1
                    if new_dist < distances.get((nx, ny), float('inf')):
                        distances[(nx, ny)] = new_dist
                        heapq.heappush(pq, (new_dist, (nx, ny)))
        return float('inf')

    for i in range(rows):
        for j in range(cols):
            if grid[i, j] == 0:
                node = (i, j)
                distance = astar_distance(node, end)
                if distance != float('inf'):
                    # 特征：归一化的 x, y，5x5邻域比例，归一化曼哈顿距离
                    manhattan = (abs(i - end[0]) + abs(j - end[1])) / (rows + cols)
                    features = [i / rows, j / cols, get_neighbors_feature(node), manhattan]
                    X.append(features)
                    y.append(distance)

    return np.array(X), np.array(y)

# 训练神经网络（优化：批量训练、学习率调度、早停）


def train_model(X, y):
    """
    训练神经网络模型的函数
    
    参数:
        X: 输入特征矩阵
        y: 目标值向量（实际距离）
    返回:
        训练好的模型
    """
    # 初始化模型和训练组件
    model = HeuristicNet()  # 创建神经网络模型实例
    criterion = nn.MSELoss()  # 使用均方误差作为损失函数
    optimizer = optim.Adam(model.parameters(), lr=0.001)  # 使用Adam优化器，学习率为0.001
    
    # 学习率调度器：当损失不再下降时降低学习率
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        mode='min',  # 监控最小化指标
        factor=0.5,  # 学习率减半
        patience=10  # 等待10轮无改善后再调整
    )

    # 数据转换为PyTorch张量
    X_tensor = torch.FloatTensor(X)
    y_tensor = torch.FloatTensor(y).reshape(-1, 1)
    
    # 训练参数设置
    batch_size = 16  # 小批量训练的大小
    n_samples = X.shape[0]  # 样本总数
    indices = np.arange(n_samples)  # 用于随机打乱数据的索引

    # 设置训练模式
    model.train()
    epochs = 200  # 最大训练轮数
    best_loss = float('inf')  # 记录最佳损失值
    patience = 20  # 早停耐心值
    patience_counter = 0  # 早停计数器
    losses = []  # 记录每轮的损失值

    # 使用tqdm创建进度条
    pbar = tqdm(range(epochs), desc='训练进度')
    for epoch in pbar:
        # 随机打乱训练数据
        np.random.shuffle(indices)
        epoch_loss = 0

        # 小批量训练
        for i in range(0, n_samples, batch_size):
            batch_indices = indices[i:i + batch_size]
            X_batch = X_tensor[batch_indices]
            y_batch = y_tensor[batch_indices]

            # 前向传播和反向传播
            optimizer.zero_grad()  # 清空梯度
            outputs = model(X_batch)  # 前向传播
            loss = criterion(outputs, y_batch)  # 计算损失
            
            # 添加L1正则化以防止过拟合
            l1_lambda = 0.001  # L1正则化系数
            l1_norm = sum(p.abs().sum() for p in model.parameters())
            loss = loss + l1_lambda * l1_norm
            
            loss.backward()  # 反向传播
            optimizer.step()  # 更新参数
            
            # 累加批次损失
            epoch_loss += loss.item() * len(batch_indices)

        # 计算平均损失
        epoch_loss /= n_samples
        losses.append(epoch_loss)
        
        # 更新学习率
        scheduler.step(epoch_loss)

        # 早停检查
        if epoch_loss < best_loss:
            best_loss = epoch_loss
            patience_counter = 0
        else:
            patience_counter += 1
        if patience_counter >= patience:
            print(f"早停于第 {epoch + 1} 轮")
            break

        # 更新进度条信息
        pbar.set_postfix({'loss': f'{epoch_loss:.4f}'})

    # 绘制损失曲线
    plt.figure(figsize=(8, 4))
    plt.plot(losses)
    plt.title('训练损失曲线')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.grid(True)
    plt.show()

    return model

# 预计算邻域特征以加速推理
def precompute_neighbor_features(grid):
    rows, cols = grid.shape
    neighbor_features = np.zeros((rows, cols))
    for i in range(rows):
        for j in range(cols):
            count = 0
            total = 0
            for dx in [-2, -1, 0, 1, 2]:
                for dy in [-2, -1, 0, 1, 2]:
                    nx, ny = i + dx, j + dy
                    if 0 <= nx < rows and 0 <= ny < cols:
                        count += grid[nx, ny]
                        total += 1
            neighbor_features[i, j] = count / total if total > 0 else 0
    return neighbor_features

# 生成并训练模型
X_train, y_train = generate_training_data(grid, end)
model = train_model(X_train, y_train)
model.eval()
neighbor_features = precompute_neighbor_features(grid)

# A*算法（使用神经网络预测启发式函数）
def astar_with_steps(grid, start, end):
    start_time = time.perf_counter()  # 使用更高精度的计时器
    step_times = []  # 记录每一步时间和截至该步的总时间（格式：(step_duration, total_so_far)）

    rows, cols = grid.shape
    distances = {(i, j): float('inf') for i in range(rows) for j in range(cols)}
    distances[start] = 0
    previous = {(i, j): None for i in range(rows) for j in range(cols)}
    pq = [(0, 0, start)]  # (f_score, g_score, node)
    visited = []
    explored = []  # 记录探索顺序

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    # 曼哈顿距离作为备用
    def manhattan_distance(node):
        return abs(node[0] - end[0]) + abs(node[1] - end[1])

    # 使用神经网络预测启发式距离
    def heuristic(node):
        x, y = node
        # 使用预计算的邻域特征
        neighbor_feature = neighbor_features[x, y]
        manhattan = (abs(x - end[0]) + abs(y - end[1])) / (rows + cols)
        features = np.array([[x / rows, y / cols, neighbor_feature, manhattan]])
        features_tensor = torch.FloatTensor(features)
        with torch.no_grad():
            h_score = model(features_tensor).item()
        # 确保启发式值非负且可接受
        h_score = max(0, h_score)
        manhattan_dist = manhattan_distance(node)
        if h_score > manhattan_dist * 1.5:  # 限制高估
            h_score = manhattan_dist
        return h_score

    while pq:
        step_start = time.perf_counter()  # 记录每步开始时间
        _, current_g, current = heapq.heappop(pq)
        if current in set(visited):
            continue
        visited.append(current)
        explored.append(current)
        step_duration = time.perf_counter() - step_start  # 本步耗时
        total_so_far = time.perf_counter() - start_time  # 截至当前的总时间
        step_times.append((step_duration, total_so_far))  # 记录每步时间和总时间

        if current == end:
            break

        for dx, dy in directions:
            next_x, next_y = current[0] + dx, current[1] + dy
            neighbor = (next_x, next_y)
            if (0 <= next_x < rows and 0 <= next_y < cols and
                    grid[next_x, next_y] == 0 and neighbor not in set(visited)):
                new_g = current_g + 1  # 每步成本为 1
                if new_g < distances[neighbor]:
                    distances[neighbor] = new_g
                    previous[neighbor] = current
                    h_score = heuristic(neighbor)
                    f_score = new_g + h_score
                    heapq.heappush(pq, (f_score, new_g, neighbor))

    # 重建路径
    path = []
    current = end
    while current is not None:
        path.append(current)
        current = previous[current]
    path.reverse()
    total_time = time.perf_counter() - start_time  # 计算总时间
    return path if distances[end] != float('inf') else None, explored, step_times, total_time

# 可视化函数（动态展示）
def animate_pathfinding(grid, start, end, path, explored, step_times, total_time):
    # 创建两个图形窗口
    fig_vis, ax_vis = plt.subplots(figsize=(8, 8))  # 路径可视化窗口
    fig_info, ax_info = plt.subplots(figsize=(4, 3))  # 信息显示窗口
    
    # 设置路径可视化窗口
    ax_vis.set_title("优化后的 A* with PyTorch 路径搜索可视化", fontsize=12)
    ax_vis.imshow(grid, cmap=plt.colormaps['Greys'], interpolation='nearest')
    
    # 设置网格线
    ax_vis.grid(True, which='both', color='black', linestyle='-', linewidth=0.5)
    ax_vis.set_xticks(np.arange(-0.5, grid.shape[1], 1))
    ax_vis.set_yticks(np.arange(-0.5, grid.shape[0], 1))
    ax_vis.set_xticklabels([])
    ax_vis.set_yticklabels([])

    # 初始化起点、终点和路径
    start_point, = ax_vis.plot(start[1], start[0], 'go', label='起点', markersize=10)
    end_point, = ax_vis.plot(end[1], end[0], 'ro', label='终点', markersize=10)
    path_line, = ax_vis.plot([], [], 'b-', label='最短路径', linewidth=2)
    
    # 创建一个空的绘图对象列表，用于动态更新探索节点
    explored_plots = []
    
    # 将路径转换为集合以加速查找
    path_set = set(path)
    
    ax_vis.legend(loc='upper right')

    # 设置信息显示窗口
    ax_info.set_axis_off()  # 隐藏坐标轴
    info_text = ax_info.text(0.05, 0.95, '',
                            transform=ax_info.transAxes,
                            bbox=dict(facecolor='white',
                                    alpha=0.8,
                                    edgecolor='gray',
                                    boxstyle='round,pad=0.5'),
                            fontsize=10,
                            verticalalignment='top')

    # 动画更新函数
    def update(frame):
        nonlocal explored_plots
        
        # 清除旧的探索节点绘图对象
        for plot in explored_plots:
            plot.remove()
        explored_plots = []
        
        if frame < len(explored):
            # 绘制所有已探索的节点，根据是否在路径上设置颜色
            for i, node in enumerate(explored[:frame + 1]):
                alpha = max(0.5, 1.0 - (frame - i) * 0.05)  # 最新节点 alpha=1.0，较旧节点逐渐变淡
                # 如果节点在最短路径上，标为红色；否则标为黄色
                color = 'rx' if node in path_set else 'yx'
                plot, = ax_vis.plot(node[1], node[0], color, markersize=8, alpha=alpha)
                explored_plots.append(plot)
            
            step_duration, total_so_far = step_times[frame]  # 获取每步时间和截至当前的总时间
            current_text = (
                "实时搜索信息\n"
                "──────────\n"
                f"当前步数: {frame+1}\n"
                f"已探索节点: {len(explored[:frame+1])}\n"
                f"当前步耗时: {step_duration:.7f}秒\n"
                f"截至当前总耗时: {total_so_far:.6f}秒\n"
            )
        elif frame == len(explored) and path:
            # 绘制最短路径
            path_x, path_y = zip(*path)
            path_line.set_data(path_y, path_x)
            
            # 保持所有探索节点可见，路径上的节点为红色
            for i, node in enumerate(explored):
                alpha = max(0.5, 1.0 - (len(explored) - 1 - i) * 0.05)
                color = 'rx' if node in path_set else 'yx'
                plot, = ax_vis.plot(node[1], node[0], color, markersize=8, alpha=alpha)
                explored_plots.append(plot)
            
            _, final_total = step_times[-1] if step_times else (0, total_time)
            current_text = (
                "搜索完成！\n"
                "──────────\n"
                f"总步数: {len(explored)}\n"
                f"路径长度: {len(path)}\n"
                f"算法总耗时: {total_time:.6f}秒"
            )
        
        info_text.set_text(current_text)
        fig_info.canvas.draw()
        
        return [start_point, end_point, path_line] + explored_plots

    # 调整布局
    fig_vis.tight_layout()
    fig_info.tight_layout()

    # 创建动画
    frames = len(explored) + 1
    ani = FuncAnimation(fig_vis, update, frames=frames, interval=200,
                       blit=True, repeat=False)

    plt.show()

# 主程序
path, explored, step_times, total_time = astar_with_steps(grid, start, end)
if path:
    print(f"找到的最短路径: {path}")
    print(f"路径长度: {len(path)}")
    print(f"总探索步数: {len(explored)}")
    _, final_total = step_times[-1] if step_times else (0, total_time)
    print(f"算法总耗时: {total_time:.6f}秒")
    animate_pathfinding(grid, start, end, path, explored, step_times, total_time)
else:
    print("无法找到路径！")