"""
经验回放缓冲区 - 完整实现
包含三种缓冲区：
1. ReplayBuffer - 基础均匀采样
2. PrioritizedReplayBuffer - 优先经验回放 (PER)
3. HindsightReplayBuffer - 后见之明经验回放 (HER)
"""
import numpy as np
import random
from collections import deque
from typing import Tuple, List
import torch


# =====================================================================
# 1. 基础经验回放缓冲区 (Uniform Random Sampling)
# =====================================================================

class ReplayBuffer:
    """
    基础经验回放缓冲区
    使用均匀随机采样策略
    """
    
    def __init__(self, capacity: int):
        """
        Args:
            capacity: 缓冲区容量
        """
        self.buffer = deque(maxlen=capacity)
        self.capacity = capacity
    
    def push(self, state, action, reward, next_state, done):
        """
        添加经验
        
        Args:
            state: 当前状态
            action: 执行的动作
            reward: 获得的奖励
            next_state: 下一个状态
            done: 是否终止
        """
        self.buffer.append((state, action, reward, next_state, done))
    
    def sample(self, batch_size: int) -> Tuple:
        """
        随机采样批次
        
        Args:
            batch_size: 批次大小
            
        Returns:
            (states, actions, rewards, next_states, dones)
        """
        batch = random.sample(self.buffer, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        
        return (
            np.array(states, dtype=np.float32),
            np.array(actions, dtype=np.int64),
            np.array(rewards, dtype=np.float32),
            np.array(next_states, dtype=np.float32),
            np.array(dones, dtype=np.float32)
        )
    
    def sample_tensors(self, batch_size: int, device='cpu') -> Tuple:
        """
        采样并转换为PyTorch张量
        
        Args:
            batch_size: 批次大小
            device: 设备 ('cpu' 或 'cuda')
            
        Returns:
            (states, actions, rewards, next_states, dones) 的张量
        """
        states, actions, rewards, next_states, dones = self.sample(batch_size)
        
        return (
            torch.FloatTensor(states).to(device),
            torch.LongTensor(actions).to(device),
            torch.FloatTensor(rewards).to(device),
            torch.FloatTensor(next_states).to(device),
            torch.FloatTensor(dones).to(device)
        )
    
    def __len__(self):
        """返回缓冲区当前大小"""
        return len(self.buffer)
    
    def is_ready(self, batch_size: int) -> bool:
        """检查是否有足够的样本进行采样"""
        return len(self.buffer) >= batch_size
    
    def clear(self):
        """清空缓冲区"""
        self.buffer.clear()
    
    def get_statistics(self):
        """获取缓冲区统计信息"""
        if len(self.buffer) == 0:
            return {}
        
        rewards = [exp[2] for exp in self.buffer]
        
        return {
            'size': len(self.buffer),
            'capacity': self.capacity,
            'utilization': len(self.buffer) / self.capacity,
            'avg_reward': np.mean(rewards),
            'max_reward': np.max(rewards),
            'min_reward': np.min(rewards),
            'std_reward': np.std(rewards)
        }


# =====================================================================
# 2. 优先经验回放缓冲区 (Prioritized Experience Replay)
# =====================================================================

class SumTree:
    """
    Sum Tree数据结构
    用于高效实现优先级采样
    
    树的叶子节点存储优先级，父节点存储子节点优先级之和
    """
    
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.tree = np.zeros(2 * capacity - 1)  # 存储优先级
        self.data = np.zeros(capacity, dtype=object)  # 存储实际数据
        self.write_index = 0
        self.size = 0
    
    def _propagate(self, idx: int, change: float):
        """向上传播优先级变化"""
        parent = (idx - 1) // 2
        self.tree[parent] += change
        
        if parent != 0:
            self._propagate(parent, change)
    
    def _retrieve(self, idx: int, s: float):
        """根据累积优先级检索叶子节点"""
        left = 2 * idx + 1
        right = left + 1
        
        if left >= len(self.tree):
            return idx
        
        if s <= self.tree[left]:
            return self._retrieve(left, s)
        else:
            return self._retrieve(right, s - self.tree[left])
    
    def total(self) -> float:
        """返回所有优先级之和"""
        return self.tree[0]
    
    def add(self, priority: float, data):
        """添加数据"""
        idx = self.write_index + self.capacity - 1
        
        self.data[self.write_index] = data
        self.update(idx, priority)
        
        self.write_index = (self.write_index + 1) % self.capacity
        self.size = min(self.size + 1, self.capacity)
    
    def update(self, idx: int, priority: float):
        """更新优先级"""
        change = priority - self.tree[idx]
        self.tree[idx] = priority
        self._propagate(idx, change)
    
    def get(self, s: float):
        """根据累积优先级获取数据"""
        idx = self._retrieve(0, s)
        data_idx = idx - self.capacity + 1
        
        return idx, self.tree[idx], self.data[data_idx]


class PrioritizedReplayBuffer:
    """
    优先经验回放缓冲区 (PER)
    
    根据TD误差为经验分配优先级，重要的经验被更频繁地采样
    
    参考论文: Schaul et al. "Prioritized Experience Replay" (2015)
    """
    
    def __init__(self, capacity: int, alpha: float = 0.6, beta: float = 0.4, 
                 beta_increment: float = 0.001, epsilon: float = 1e-6):
        """
        Args:
            capacity: 缓冲区容量
            alpha: 优先级指数 (0=均匀采样, 1=完全优先采样)
            beta: 重要性采样权重指数 (0=无校正, 1=完全校正)
            beta_increment: beta的增量
            epsilon: 小常数，防止优先级为0
        """
        self.tree = SumTree(capacity)
        self.capacity = capacity
        self.alpha = alpha
        self.beta = beta
        self.beta_increment = beta_increment
        self.epsilon = epsilon
        self.max_priority = 1.0
    
    def push(self, state, action, reward, next_state, done):
        """添加经验，使用最大优先级"""
        data = (state, action, reward, next_state, done)
        priority = self.max_priority ** self.alpha
        self.tree.add(priority, data)
    
    def sample(self, batch_size: int) -> Tuple:
        """
        按优先级采样
        
        Returns:
            (states, actions, rewards, next_states, dones, indices, weights)
        """
        batch = []
        indices = []
        priorities = []
        segment = self.tree.total() / batch_size
        
        # 增加beta（逐渐增加重要性采样校正）
        self.beta = min(1.0, self.beta + self.beta_increment)
        
        # 采样
        for i in range(batch_size):
            a = segment * i
            b = segment * (i + 1)
            s = random.uniform(a, b)
            
            idx, priority, data = self.tree.get(s)
            
            batch.append(data)
            indices.append(idx)
            priorities.append(priority)
        
        # 计算重要性采样权重
        sampling_probabilities = np.array(priorities) / self.tree.total()
        weights = (self.tree.size * sampling_probabilities) ** (-self.beta)
        weights = weights / weights.max()  # 归一化
        
        # 解包数据
        states, actions, rewards, next_states, dones = zip(*batch)
        
        return (
            np.array(states, dtype=np.float32),
            np.array(actions, dtype=np.int64),
            np.array(rewards, dtype=np.float32),
            np.array(next_states, dtype=np.float32),
            np.array(dones, dtype=np.float32),
            np.array(indices, dtype=np.int32),
            np.array(weights, dtype=np.float32)
        )
    
    def update_priorities(self, indices: np.ndarray, td_errors: np.ndarray):
        """
        根据TD误差更新优先级
        
        Args:
            indices: 样本索引
            td_errors: TD误差
        """
        for idx, td_error in zip(indices, td_errors):
            priority = (abs(td_error) + self.epsilon) ** self.alpha
            self.tree.update(idx, priority)
            self.max_priority = max(self.max_priority, priority)
    
    def __len__(self):
        return self.tree.size
    
    def is_ready(self, batch_size: int) -> bool:
        return self.tree.size >= batch_size


# =====================================================================
# 3. 后见之明经验回放 (Hindsight Experience Replay)
# =====================================================================

class HindsightReplayBuffer:
    """
    后见之明经验回放缓冲区 (HER)
    
    对于失败的轨迹，重新标注目标，将失败转化为成功经验
    适用于稀疏奖励环境
    
    参考论文: Andrychowicz et al. "Hindsight Experience Replay" (2017)
    """
    
    def __init__(self, capacity: int, k: int = 4, 
                 strategy: str = 'future'):
        """
        Args:
            capacity: 缓冲区容量
            k: 每个轨迹添加多少个虚拟目标
            strategy: 目标替换策略 ('future', 'final', 'episode', 'random')
        """
        self.buffer = deque(maxlen=capacity)
        self.capacity = capacity
        self.k = k
        self.strategy = strategy
        
        # 临时存储当前episode的轨迹
        self.episode_buffer = []
    
    def push(self, state, action, reward, next_state, done, 
             achieved_goal=None, desired_goal=None):
        """
        添加经验
        
        Args:
            state: 状态
            action: 动作
            reward: 奖励
            next_state: 下一个状态
            done: 是否终止
            achieved_goal: 实际达到的目标
            desired_goal: 期望的目标
        """
        self.episode_buffer.append({
            'state': state,
            'action': action,
            'reward': reward,
            'next_state': next_state,
            'done': done,
            'achieved_goal': achieved_goal,
            'desired_goal': desired_goal
        })
        
        # Episode结束时处理整个轨迹
        if done:
            self._store_episode()
    
    def _store_episode(self):
        """存储整个episode，并生成HER样本"""
        T = len(self.episode_buffer)
        
        # 1. 存储原始经验
        for transition in self.episode_buffer:
            self.buffer.append((
                transition['state'],
                transition['action'],
                transition['reward'],
                transition['next_state'],
                transition['done']
            ))
        
        # 2. 生成HER样本
        for t in range(T):
            # 为每个时间步生成k个虚拟目标
            for _ in range(self.k):
                # 根据策略选择新目标
                new_goal = self._sample_goal(t, T)
                
                if new_goal is not None:
                    # 使用新目标重新计算奖励
                    transition = self.episode_buffer[t]
                    new_reward = self._compute_reward(
                        transition['achieved_goal'], 
                        new_goal
                    )
                    
                    # 修改状态中的目标信息
                    new_state = self._replace_goal(
                        transition['state'], 
                        new_goal
                    )
                    new_next_state = self._replace_goal(
                        transition['next_state'], 
                        new_goal
                    )
                    
                    # 添加虚拟经验
                    self.buffer.append((
                        new_state,
                        transition['action'],
                        new_reward,
                        new_next_state,
                        transition['done']
                    ))
        
        # 清空episode缓冲
        self.episode_buffer = []
    
    def _sample_goal(self, t: int, T: int):
        """
        根据策略采样新目标
        
        Args:
            t: 当前时间步
            T: episode总长度
        """
        if self.strategy == 'future':
            # 从未来时间步中采样
            if t < T - 1:
                future_t = random.randint(t + 1, T - 1)
                return self.episode_buffer[future_t]['achieved_goal']
        
        elif self.strategy == 'final':
            # 使用最终状态作为目标
            return self.episode_buffer[T - 1]['achieved_goal']
        
        elif self.strategy == 'episode':
            # 从整个episode中随机采样
            random_t = random.randint(0, T - 1)
            return self.episode_buffer[random_t]['achieved_goal']
        
        elif self.strategy == 'random':
            # 完全随机生成目标（需要根据具体任务实现）
            return None  # 需要自定义
        
        return None
    
    def _compute_reward(self, achieved_goal, desired_goal):
        """
        计算新目标下的奖励
        
        这里使用简单的二元奖励：达到目标=0，否则=-1
        可以根据具体任务自定义
        """
        if achieved_goal is None or desired_goal is None:
            return -1.0
        
        # 使用欧氏距离判断是否达到目标
        distance = np.linalg.norm(
            np.array(achieved_goal) - np.array(desired_goal)
        )
        
        threshold = 0.05  # 阈值
        return 0.0 if distance < threshold else -1.0
    
    def _replace_goal(self, state, new_goal):
        """
        替换状态中的目标信息
        
        假设状态的最后几维是目标
        需要根据具体状态表示调整
        """
        if new_goal is None:
            return state
        
        # 这里假设目标维度与achieved_goal相同
        goal_dim = len(new_goal)
        new_state = state.copy()
        new_state[-goal_dim:] = new_goal
        
        return new_state
    
    def sample(self, batch_size: int) -> Tuple:
        """随机采样"""
        batch = random.sample(self.buffer, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        
        return (
            np.array(states, dtype=np.float32),
            np.array(actions, dtype=np.int64),
            np.array(rewards, dtype=np.float32),
            np.array(next_states, dtype=np.float32),
            np.array(dones, dtype=np.float32)
        )
    
    def __len__(self):
        return len(self.buffer)
    
    def is_ready(self, batch_size: int) -> bool:
        return len(self.buffer) >= batch_size


# =====================================================================
# 4. N-Step经验回放缓冲区
# =====================================================================

class NStepReplayBuffer:
    """
    N-Step经验回放缓冲区
    
    存储N步的累积奖励，加速值函数估计的传播
    """
    
    def __init__(self, capacity: int, n_step: int = 3, gamma: float = 0.99):
        """
        Args:
            capacity: 缓冲区容量
            n_step: N步回报
            gamma: 折扣因子
        """
        self.buffer = deque(maxlen=capacity)
        self.n_step = n_step
        self.gamma = gamma
        self.n_step_buffer = deque(maxlen=n_step)
    
    def push(self, state, action, reward, next_state, done):
        """添加经验"""
        self.n_step_buffer.append((state, action, reward, next_state, done))
        
        # 当缓冲区达到n步时，计算n步回报
        if len(self.n_step_buffer) == self.n_step:
            state, action = self.n_step_buffer[0][:2]
            
            # 计算n步累积奖励
            n_step_reward = 0
            for i, (_, _, r, _, d) in enumerate(self.n_step_buffer):
                n_step_reward += (self.gamma ** i) * r
                if d:
                    break
            
            # 获取n步后的状态
            _, _, _, next_state, done = self.n_step_buffer[-1]
            
            self.buffer.append((state, action, n_step_reward, next_state, done))
    
    def sample(self, batch_size: int) -> Tuple:
        """采样"""
        batch = random.sample(self.buffer, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        
        return (
            np.array(states, dtype=np.float32),
            np.array(actions, dtype=np.int64),
            np.array(rewards, dtype=np.float32),
            np.array(next_states, dtype=np.float32),
            np.array(dones, dtype=np.float32)
        )
    
    def __len__(self):
        return len(self.buffer)
    
    def is_ready(self, batch_size: int) -> bool:
        return len(self.buffer) >= batch_size


# =====================================================================
# 5. 演示和测试
# =====================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("经验回放缓冲区测试")
    print("=" * 70)
    
    # 1. 测试基础缓冲区
    print("\n1. 测试基础ReplayBuffer:")
    buffer = ReplayBuffer(capacity=1000)
    
    # 添加随机经验
    for i in range(100):
        state = np.random.randn(10)
        action = np.random.randint(0, 5)
        reward = np.random.randn()
        next_state = np.random.randn(10)
        done = np.random.rand() > 0.9
        
        buffer.push(state, action, reward, next_state, done)
    
    print(f"  缓冲区大小: {len(buffer)}")
    
    # 采样
    batch = buffer.sample(32)
    print(f"  采样批次形状: states={batch[0].shape}, actions={batch[1].shape}")
    
    # 统计信息
    stats = buffer.get_statistics()
    print(f"  统计信息: {stats}")
    
    # 2. 测试优先经验回放
    print("\n2. 测试PrioritizedReplayBuffer:")
    per_buffer = PrioritizedReplayBuffer(capacity=1000)
    
    for i in range(100):
        state = np.random.randn(10)
        action = np.random.randint(0, 5)
        reward = np.random.randn()
        next_state = np.random.randn(10)
        done = False
        
        per_buffer.push(state, action, reward, next_state, done)
    
    print(f"  缓冲区大小: {len(per_buffer)}")
    
    # 采样（包含权重）
    batch_data = per_buffer.sample(32)
    print(f"  采样批次: {len(batch_data)} 个元素")
    print(f"  重要性权重范围: [{batch_data[6].min():.3f}, {batch_data[6].max():.3f}]")
    
    # 更新优先级
    indices = batch_data[5]
    td_errors = np.random.randn(32)
    per_buffer.update_priorities(indices, td_errors)
    print(f"  ✓ 优先级已更新")
    
    # 3. 测试N-Step缓冲区
    print("\n3. 测试NStepReplayBuffer:")
    nstep_buffer = NStepReplayBuffer(capacity=1000, n_step=3)
    
    for i in range(100):
        state = np.random.randn(10)
        action = np.random.randint(0, 5)
        reward = np.random.randn()
        next_state = np.random.randn(10)
        done = i % 20 == 19  # 每20步结束一次
        
        nstep_buffer.push(state, action, reward, next_state, done)
    
    print(f"  缓冲区大小: {len(nstep_buffer)}")
    
    if nstep_buffer.is_ready(32):
        batch = nstep_buffer.sample(32)
        print(f"  采样成功: {batch[0].shape}")
    
    print("\n" + "=" * 70)
    print("所有测试通过！")
    print("=" * 70)