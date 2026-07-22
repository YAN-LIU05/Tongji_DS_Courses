"""
反爬虫环境 - anti_spider_env.py
模拟网站的反爬虫机制
"""
import numpy as np
import gymnasium as gym
from gymnasium import spaces
import random


class AntiSpiderEnvironment(gym.Env):
    """反爬虫环境"""
    
    def __init__(self, config):
        """
        初始化环境
        
        Args:
            config: 配置字典或Config对象
        """
        super().__init__()
        
        # 处理config对象或字典
        if hasattr(config, '__dict__'):
            # 如果是对象，转换为字典
            config_dict = config.__dict__ if hasattr(config, '__dict__') else {}
            # 或者使用 getattr 获取属性
            self.ip_pool_size = getattr(config, 'ip_pool_size', 100)
            self.max_requests = getattr(config, 'max_requests', 1000)
            self.detection_threshold = getattr(config, 'detection_threshold', 0.7)
            self.ban_penalty = getattr(config, 'ban_penalty', -10)
            self.success_reward = getattr(config, 'success_reward', 1)
        else:
            # 如果是字典
            self.ip_pool_size = config.get('ip_pool_size', 100)
            self.max_requests = config.get('max_requests', 1000)
            self.detection_threshold = config.get('detection_threshold', 0.7)
            self.ban_penalty = config.get('ban_penalty', -10)
            self.success_reward = config.get('success_reward', 1)
        
        self.config = config
        
        # 环境状态变量
        self.current_step = 0
        self.current_ip = 0
        self.request_count = 0
        self.ban_count = 0
        self.success_count = 0
        self.detection_level = 0.0
        
        # 定义观察空间 (归一化后的状态)
        # [当前IP索引, 请求计数, 检测等级, 成功率, 封禁率]
        self.observation_space = spaces.Box(
            low=0.0,
            high=1.0,
            shape=(5,),
            dtype=np.float32
        )
        
        # 定义动作空间
        # 0: 继续当前IP
        # 1: 切换到新IP
        # 2: 降低请求频率
        # 3: 改变请求模式
        self.action_space = spaces.Discrete(4)
        
        # IP状态追踪
        self.ip_states = {}
        
        # 初始化环境
        self.reset()
    
    def reset(self, seed=None, options=None):
        """
        重置环境
        
        Args:
            seed: 随机种子
            options: 可选参数
            
        Returns:
            observation, info
        """
        super().reset(seed=seed)
        
        # 重置环境状态
        self.current_step = 0
        self.current_ip = random.randint(0, self.ip_pool_size - 1)
        self.request_count = 0
        self.ban_count = 0
        self.success_count = 0
        self.detection_level = 0.0
        
        # 重置IP状态
        self.ip_states = {}
        for i in range(self.ip_pool_size):
            self.ip_states[i] = {
                'requests': 0,
                'detection': 0.0,
                'banned': False
            }
        
        observation = self._get_observation()
        info = self._get_info()
        
        return observation, info
    
    def _get_observation(self):
        """
        获取当前观察
        
        Returns:
            归一化的状态向量
        """
        current_ip_state = self.ip_states.get(self.current_ip, {
            'requests': 0,
            'detection': 0.0,
            'banned': False
        })
        
        # 计算成功率和封禁率
        success_rate = self.success_count / max(1, self.request_count)
        ban_rate = self.ban_count / max(1, self.request_count)
        
        observation = np.array([
            self.current_ip / self.ip_pool_size,
            self.request_count / self.max_requests,
            current_ip_state['detection'],
            success_rate,
            ban_rate
        ], dtype=np.float32)
        
        return observation
    
    def _get_info(self):
        """获取额外信息"""
        return {
            'current_step': self.current_step,
            'current_ip': self.current_ip,
            'request_count': self.request_count,
            'success_count': self.success_count,
            'ban_count': self.ban_count,
            'detection_level': self.detection_level
        }
    
    def step(self, action):
        """
        执行动作
        
        Args:
            action: 动作编号
            
        Returns:
            observation, reward, terminated, truncated, info
        """
        self.current_step += 1
        reward = 0
        terminated = False
        truncated = False
        
        current_ip_state = self.ip_states[self.current_ip]
        
        # 执行动作
        if action == 0:
            reward = self._continue_current_ip(current_ip_state)
        elif action == 1:
            reward = self._switch_ip()
        elif action == 2:
            reward = self._reduce_frequency(current_ip_state)
        elif action == 3:
            reward = self._change_pattern(current_ip_state)
        
        # 更新检测等级
        self._update_detection_level()
        
        # 检查终止条件
        if self.current_step >= self.max_requests:
            truncated = True
        
        if self.ban_count > self.ip_pool_size * 0.8:
            terminated = True
            reward += self.ban_penalty
        
        observation = self._get_observation()
        info = self._get_info()
        
        return observation, reward, terminated, truncated, info
    
    def _continue_current_ip(self, ip_state):
        """继续使用当前IP"""
        reward = 0
        
        if ip_state['banned']:
            reward = self.ban_penalty
            self.ban_count += 1
        else:
            ip_state['requests'] += 1
            self.request_count += 1
            
            detection_prob = min(0.9, ip_state['detection'] + 
                                np.random.uniform(0.01, 0.05))
            ip_state['detection'] = detection_prob
            
            if np.random.random() < detection_prob:
                if detection_prob > self.detection_threshold:
                    ip_state['banned'] = True
                    reward = self.ban_penalty
                    self.ban_count += 1
                else:
                    reward = -1
            else:
                reward = self.success_reward
                self.success_count += 1
        
        return reward
    
    def _switch_ip(self):
        """切换IP"""
        available_ips = [ip for ip, state in self.ip_states.items() 
                        if not state['banned'] and ip != self.current_ip]
        
        if available_ips:
            self.current_ip = random.choice(available_ips)
            return -0.1
        else:
            return self.ban_penalty
    
    def _reduce_frequency(self, ip_state):
        """降低请求频率"""
        reward = 0
        
        if ip_state['banned']:
            reward = self.ban_penalty
            self.ban_count += 1
        else:
            ip_state['detection'] = max(0.0, ip_state['detection'] - 0.1)
            ip_state['requests'] += 1
            self.request_count += 1
            
            if np.random.random() > ip_state['detection'] * 0.5:
                reward = self.success_reward
                self.success_count += 1
            else:
                reward = -0.5
        
        return reward
    
    def _change_pattern(self, ip_state):
        """改变请求模式"""
        reward = 0
        
        if ip_state['banned']:
            reward = self.ban_penalty
            self.ban_count += 1
        else:
            ip_state['detection'] = max(0.0, ip_state['detection'] - 0.15)
            ip_state['requests'] += 1
            self.request_count += 1
            
            if np.random.random() > ip_state['detection'] * 0.3:
                reward = self.success_reward * 1.2
                self.success_count += 1
            else:
                reward = -0.3
        
        return reward
    
    def _update_detection_level(self):
        """更新全局检测等级"""
        total_detection = sum(state['detection'] for state in self.ip_states.values())
        self.detection_level = total_detection / self.ip_pool_size
    
    def render(self):
        """渲染环境"""
        print(f"\n{'='*60}")
        print(f"步数: {self.current_step}/{self.max_requests}")
        print(f"当前IP: {self.current_ip}")
        print(f"请求数: {self.request_count}, 成功: {self.success_count}, 封禁: {self.ban_count}")
        print(f"成功率: {self.success_count / max(1, self.request_count):.2%}")
        print(f"检测等级: {self.detection_level:.2f}")
        print(f"{'='*60}\n")
    
    def close(self):
        """关闭环境"""
        pass


def make_anti_spider_env(config=None):
    """
    创建反爬虫环境
    
    Args:
        config: 配置字典或Config对象
        
    Returns:
        环境实例
    """
    if config is None:
        config = {
            'ip_pool_size': 100,
            'max_requests': 1000,
            'detection_threshold': 0.7,
            'ban_penalty': -10,
            'success_reward': 1
        }
    
    return AntiSpiderEnvironment(config)


"""
改进的反爬虫环境 - 更真实的反爬虫机制
包括：频率检测、行为模式识别、IP信誉系统、验证码机制等
"""
import numpy as np
import gymnasium as gym
from gymnasium import spaces
import random
from collections import deque, defaultdict
import time


class RealisticAntiSpiderEnvironment(gym.Env):
    """真实的反爬虫环境"""
    
    def __init__(self, config):
        """
        初始化环境
        
        Args:
            config: 配置字典
        """
        super().__init__()
        
        # 配置参数
        if hasattr(config, '__dict__'):
            self.ip_pool_size = getattr(config, 'ip_pool_size', 50)
            self.max_requests = getattr(config, 'max_requests', 1000)
            self.ua_pool_size = getattr(config, 'ua_pool_size', 20)
        else:
            self.ip_pool_size = config.get('ip_pool_size', 50)
            self.max_requests = config.get('max_requests', 1000)
            self.ua_pool_size = config.get('ua_pool_size', 20)
        
        self.config = config
        
        # === 反爬虫检测参数 ===
        # 频率检测
        self.freq_window = 60  # 检测时间窗口（秒）
        self.normal_freq_max = 10  # 正常用户60秒内最多请求数
        self.suspicious_freq = 20  # 可疑频率阈值
        self.ban_freq = 30  # 封禁频率阈值
        
        # 行为模式检测
        self.min_interval = 0.5  # 最小请求间隔（秒）
        self.pattern_window = 20  # 行为模式检测窗口
        self.pattern_threshold = 0.8  # 模式相似度阈值
        
        # IP信誉系统
        self.ip_reputation_decay = 0.95  # 信誉恢复速度
        self.reputation_threshold = 0.3  # 低信誉阈值
        
        # 验证码系统
        self.captcha_base_prob = 0.05  # 基础验证码概率
        self.captcha_solve_prob = 0.7  # 验证码解决概率
        
        # 会话管理
        self.session_timeout = 300  # 会话超时（秒）
        
        # 环境状态变量
        self.current_step = 0
        self.current_ip = 0
        self.current_ua = 0
        self.request_count = 0
        self.ban_count = 0
        self.success_count = 0
        self.captcha_count = 0
        self.timeout_count = 0
        
        # 时间戳（模拟）
        self.virtual_time = 0.0
        self.last_request_time = 0.0
        
        # IP状态追踪
        self.ip_states = {}
        self.ua_states = {}
        
        # 请求历史（用于模式检测）
        self.request_history = deque(maxlen=self.pattern_window)
        self.interval_history = deque(maxlen=self.pattern_window)
        
        # 每个IP的请求时间戳
        self.ip_request_times = defaultdict(lambda: deque(maxlen=100))
        
        # 观察空间 [12维]
        # [当前IP信誉, 当前UA年龄, 最近频率, 平均间隔, 模式分数,
        #  连续成功, 连续失败, 验证码遇到率, IP使用率, 
        #  时间进度, 总成功率, 风险评分]
        self.observation_space = spaces.Box(
            low=0.0,
            high=1.0,
            shape=(12,),
            dtype=np.float32
        )
        
        # 动作空间 [9个动作]
        # 0: 快速请求(0.5s)
        # 1: 正常请求(1-2s)
        # 2: 慢速请求(3-5s)
        # 3: 换IP继续
        # 4: 换UA继续
        # 5: 全换(IP+UA)
        # 6: 等待冷却(10s)
        # 7: 长等待+换IP(15s)
        # 8: 紧急避险(30s+全换)
        self.action_space = spaces.Discrete(9)
        
        # 初始化
        self.reset()
    
    def reset(self, seed=None, options=None):
        """重置环境"""
        super().reset(seed=seed)
        
        # 重置计数器
        self.current_step = 0
        self.current_ip = random.randint(0, self.ip_pool_size - 1)
        self.current_ua = random.randint(0, self.ua_pool_size - 1)
        self.request_count = 0
        self.ban_count = 0
        self.success_count = 0
        self.captcha_count = 0
        self.timeout_count = 0
        
        # 重置时间
        self.virtual_time = 0.0
        self.last_request_time = 0.0
        
        # 重置IP状态
        self.ip_states = {}
        for i in range(self.ip_pool_size):
            self.ip_states[i] = {
                'reputation': 1.0,  # 信誉分数
                'request_count': 0,
                'ban_count': 0,
                'last_ban_time': -999,
                'consecutive_fails': 0,
                'total_requests': 0,
                'is_banned': False,
                'ban_until': 0.0
            }
        
        # 重置UA状态
        self.ua_states = {}
        for i in range(self.ua_pool_size):
            self.ua_states[i] = {
                'age': 0,
                'request_count': 0,
                'suspicious': False
            }
        
        # 清空历史
        self.request_history.clear()
        self.interval_history.clear()
        self.ip_request_times.clear()
        
        observation = self._get_observation()
        info = self._get_info()
        
        return observation, info
    
    def _get_observation(self):
        """获取当前观察"""
        ip_state = self.ip_states[self.current_ip]
        ua_state = self.ua_states[self.current_ua]
        
        # 计算最近频率
        recent_freq = self._get_recent_frequency()
        
        # 计算平均间隔
        avg_interval = np.mean(list(self.interval_history)) if len(self.interval_history) > 0 else 1.0
        avg_interval_norm = min(1.0, avg_interval / 10.0)
        
        # 计算模式分数
        pattern_score = self._calculate_pattern_score()
        
        # 连续成功/失败
        consecutive_success = min(1.0, ip_state.get('consecutive_success', 0) / 10.0)
        consecutive_fails = min(1.0, ip_state['consecutive_fails'] / 5.0)
        
        # 验证码遇到率
        captcha_rate = self.captcha_count / max(1, self.request_count)
        
        # IP使用率
        ip_usage = sum(1 for s in self.ip_states.values() if s['total_requests'] > 0) / self.ip_pool_size
        
        # 时间进度
        time_progress = self.current_step / self.max_requests
        
        # 总成功率
        success_rate = self.success_count / max(1, self.request_count)
        
        # 风险评分
        risk_score = self._calculate_risk_score()
        
        observation = np.array([
            ip_state['reputation'],
            min(1.0, ua_state['age'] / 100.0),
            recent_freq,
            avg_interval_norm,
            pattern_score,
            consecutive_success,
            consecutive_fails,
            captcha_rate,
            ip_usage,
            time_progress,
            success_rate,
            risk_score
        ], dtype=np.float32)
        
        return observation
    
    def _get_info(self):
        """获取额外信息"""
        return {
            'current_step': self.current_step,
            'current_ip': self.current_ip,
            'current_ua': self.current_ua,
            'request_count': self.request_count,
            'success_count': self.success_count,
            'ban_count': self.ban_count,
            'captcha_count': self.captcha_count,
            'timeout_count': self.timeout_count,
            'success_rate': self.success_count / max(1, self.request_count),
            'risk_score': self._calculate_risk_score()
        }
    
    def step(self, action):
        """执行动作"""
        self.current_step += 1
        reward = 0
        terminated = False
        truncated = False
        
        # 解析动作
        interval, change_ip, change_ua = self._parse_action(action)
        
        # 更新虚拟时间
        self.virtual_time += interval
        
        # 如果需要换IP/UA
        if change_ip:
            self.current_ip = self._select_new_ip()
            reward -= 0.2  # 换IP有成本
        
        if change_ua:
            self.current_ua = self._select_new_ua()
            reward -= 0.1  # 换UA有成本
        
        # 更新UA年龄
        self.ua_states[self.current_ua]['age'] += 1
        
        # 执行请求
        request_result = self._make_request(interval)
        
        # 根据结果给奖励
        if request_result == 'success':
            reward += 1.0
            self.success_count += 1
            self.ip_states[self.current_ip]['consecutive_fails'] = 0
            self.ip_states[self.current_ip]['consecutive_success'] = \
                self.ip_states[self.current_ip].get('consecutive_success', 0) + 1
            
            # 效率奖励（快速成功）
            if interval < 2.0:
                reward += 0.2
        
        elif request_result == 'banned':
            reward -= 5.0
            self.ban_count += 1
            self.ip_states[self.current_ip]['consecutive_fails'] += 1
            self.ip_states[self.current_ip]['consecutive_success'] = 0
        
        elif request_result == 'captcha':
            reward -= 2.0
            self.captcha_count += 1
            
            # 尝试解决验证码
            if random.random() < self.captcha_solve_prob:
                reward += 0.5  # 解决了验证码
                self.success_count += 1
            else:
                reward -= 1.0  # 验证码解决失败
        
        elif request_result == 'timeout':
            reward -= 1.0
            self.timeout_count += 1
            self.ip_states[self.current_ip]['consecutive_fails'] += 1
        
        elif request_result == 'rate_limited':
            reward -= 3.0
            self.ip_states[self.current_ip]['consecutive_fails'] += 1
        
        # 等待时间惩罚（鼓励效率）
        if interval > 5.0:
            reward -= (interval - 5.0) * 0.05
        
        # 更新请求计数
        self.request_count += 1
        self.last_request_time = self.virtual_time
        
        # 记录请求历史
        self.request_history.append({
            'ip': self.current_ip,
            'ua': self.current_ua,
            'interval': interval,
            'result': request_result
        })
        self.interval_history.append(interval)
        
        # 检查终止条件
        if self.current_step >= self.max_requests:
            truncated = True
        
        # 如果太多IP被封禁
        banned_ips = sum(1 for s in self.ip_states.values() if s['is_banned'])
        if banned_ips > self.ip_pool_size * 0.7:
            terminated = True
            reward -= 10.0
        
        # 如果成功率太低
        if self.request_count > 50:
            current_success_rate = self.success_count / self.request_count
            if current_success_rate < 0.1:
                terminated = True
                reward -= 10.0
        
        observation = self._get_observation()
        info = self._get_info()
        
        return observation, reward, terminated, truncated, info
    
    def _parse_action(self, action):
        """解析动作"""
        action_map = {
            0: (0.5, False, False),   # 快速请求
            1: (random.uniform(1, 2), False, False),  # 正常请求
            2: (random.uniform(3, 5), False, False),  # 慢速请求
            3: (1.0, True, False),    # 换IP
            4: (1.0, False, True),    # 换UA
            5: (1.5, True, True),     # 全换
            6: (10.0, False, False),  # 等待冷却
            7: (15.0, True, False),   # 长等待+换IP
            8: (30.0, True, True),    # 紧急避险
        }
        return action_map.get(action, (1.0, False, False))
    
    def _select_new_ip(self):
        """选择新IP（智能选择）"""
        # 优先选择信誉高、未被封禁的IP
        available_ips = []
        for ip_id, state in self.ip_states.items():
            if ip_id == self.current_ip:
                continue
            
            if not state['is_banned'] and state['reputation'] > 0.3:
                # 权重 = 信誉 * (1 - 使用频率)
                weight = state['reputation'] * (1 - min(1.0, state['total_requests'] / 100.0))
                available_ips.append((ip_id, weight))
        
        if not available_ips:
            # 如果没有好的IP，随机选择未封禁的
            available_ips = [(ip_id, 1.0) for ip_id, state in self.ip_states.items() 
                           if not state['is_banned'] and ip_id != self.current_ip]
        
        if not available_ips:
            return self.current_ip
        
        # 加权随机选择
        ip_ids, weights = zip(*available_ips)
        weights = np.array(weights)
        weights = weights / weights.sum()
        
        return np.random.choice(ip_ids, p=weights)
    
    def _select_new_ua(self):
        """选择新UA"""
        # 优先选择使用次数少的UA
        available_uas = []
        for ua_id, state in self.ua_states.items():
            if ua_id == self.current_ua:
                continue
            weight = 1.0 / (1.0 + state['request_count'] / 10.0)
            available_uas.append((ua_id, weight))
        
        if not available_uas:
            return random.randint(0, self.ua_pool_size - 1)
        
        ua_ids, weights = zip(*available_uas)
        weights = np.array(weights)
        weights = weights / weights.sum()
        
        return np.random.choice(ua_ids, p=weights)
    
    def _make_request(self, interval):
        """
        模拟发送请求
        
        Returns:
            'success', 'banned', 'captcha', 'timeout', 'rate_limited'
        """
        ip_state = self.ip_states[self.current_ip]
        
        # 1. 检查IP是否被封禁
        if ip_state['is_banned']:
            if self.virtual_time < ip_state['ban_until']:
                return 'banned'
            else:
                # 解封
                ip_state['is_banned'] = False
                ip_state['reputation'] = max(0.3, ip_state['reputation'])
        
        # 2. 记录请求时间
        self.ip_request_times[self.current_ip].append(self.virtual_time)
        ip_state['total_requests'] += 1
        self.ua_states[self.current_ua]['request_count'] += 1
        
        # 3. 频率检测
        recent_requests = [t for t in self.ip_request_times[self.current_ip] 
                          if self.virtual_time - t <= self.freq_window]
        request_freq = len(recent_requests)
        
        # 4. 计算检测概率
        detection_prob = 0.0
        
        # 频率因素
        if request_freq > self.ban_freq:
            detection_prob += 0.9
        elif request_freq > self.suspicious_freq:
            detection_prob += 0.6
        elif request_freq > self.normal_freq_max:
            detection_prob += 0.3
        
        # 间隔因素（太快或太规律都可疑）
        if interval < self.min_interval:
            detection_prob += 0.4
        
        # 模式因素
        pattern_score = self._calculate_pattern_score()
        if pattern_score > self.pattern_threshold:
            detection_prob += 0.3
        
        # 信誉因素
        if ip_state['reputation'] < self.reputation_threshold:
            detection_prob += 0.4
        
        # UA因素（太新或太老都可疑）
        ua_age = self.ua_states[self.current_ua]['age']
        if ua_age < 3 or ua_age > 200:
            detection_prob += 0.2
        
        # 连续失败因素
        if ip_state['consecutive_fails'] > 3:
            detection_prob += 0.3
        
        # 5. 决定结果
        detection_prob = min(0.95, detection_prob)
        
        if random.random() < detection_prob:
            # 被检测到
            
            # 决定是封禁、验证码还是限流
            if detection_prob > 0.7 or ip_state['consecutive_fails'] > 5:
                # 封禁
                ip_state['is_banned'] = True
                ip_state['ban_until'] = self.virtual_time + random.uniform(100, 300)
                ip_state['ban_count'] += 1
                ip_state['reputation'] *= 0.5
                return 'banned'
            
            elif detection_prob > 0.4:
                # 验证码
                captcha_prob = self.captcha_base_prob + detection_prob * 0.5
                if random.random() < captcha_prob:
                    ip_state['reputation'] *= 0.9
                    return 'captcha'
            
            # 限流
            ip_state['reputation'] *= 0.8
            return 'rate_limited'
        
        # 6. 成功，但可能超时
        if random.random() < 0.05:  # 5%网络超时
            return 'timeout'
        
        # 7. 成功！恢复信誉
        ip_state['reputation'] = min(1.0, ip_state['reputation'] * self.ip_reputation_decay + 0.05)
        
        return 'success'
    
    def _get_recent_frequency(self):
        """获取最近的请求频率（归一化）"""
        if self.current_ip not in self.ip_request_times:
            return 0.0
        
        recent_requests = [t for t in self.ip_request_times[self.current_ip] 
                          if self.virtual_time - t <= self.freq_window]
        
        freq = len(recent_requests) / self.normal_freq_max
        return min(1.0, freq)
    
    def _calculate_pattern_score(self):
        """计算请求模式的规律性（越高越像机器人）"""
        if len(self.interval_history) < 3:
            return 0.0
        
        intervals = list(self.interval_history)
        
        # 计算间隔的标准差（越小越规律）
        std = np.std(intervals)
        mean = np.mean(intervals)
        
        if mean == 0:
            return 1.0
        
        cv = std / mean  # 变异系数
        
        # CV越小，模式越规律
        pattern_score = 1.0 / (1.0 + cv * 2)
        
        return min(1.0, pattern_score)
    
    def _calculate_risk_score(self):
        """计算当前风险分数"""
        ip_state = self.ip_states[self.current_ip]
        
        # 多因素风险评估
        risk = 0.0
        
        # IP信誉
        risk += (1.0 - ip_state['reputation']) * 0.3
        
        # 频率
        recent_freq = self._get_recent_frequency()
        risk += recent_freq * 0.2
        
        # 模式规律性
        pattern = self._calculate_pattern_score()
        risk += pattern * 0.2
        
        # 连续失败
        fail_risk = min(1.0, ip_state['consecutive_fails'] / 5.0)
        risk += fail_risk * 0.2
        
        # 封禁历史
        ban_risk = min(1.0, ip_state['ban_count'] / 3.0)
        risk += ban_risk * 0.1
        
        return min(1.0, risk)
    
    def render(self):
        """渲染环境状态"""
        print(f"\n{'='*70}")
        print(f"步数: {self.current_step}/{self.max_requests} | 虚拟时间: {self.virtual_time:.1f}s")
        print(f"当前IP: {self.current_ip} (信誉: {self.ip_states[self.current_ip]['reputation']:.2f})")
        print(f"当前UA: {self.current_ua}")
        print(f"请求: {self.request_count} | 成功: {self.success_count} ({self.success_count/max(1,self.request_count):.1%})")
        print(f"封禁: {self.ban_count} | 验证码: {self.captcha_count} | 超时: {self.timeout_count}")
        print(f"风险评分: {self._calculate_risk_score():.2f}")
        
        # IP池状态
        banned = sum(1 for s in self.ip_states.values() if s['is_banned'])
        print(f"IP池: {banned}/{self.ip_pool_size} 被封禁")
        print(f"{'='*70}\n")
    
    def close(self):
        """关闭环境"""
        pass


def make_realistic_anti_spider_env(config=None):
    """
    创建真实的反爬虫环境
    
    Args:
        config: 配置字典
        
    Returns:
        环境实例
    """
    if config is None:
        config = {
            'ip_pool_size': 50,
            'max_requests': 1000,
            'ua_pool_size': 20
        }
    
    return RealisticAntiSpiderEnvironment(config)


"""
地狱级反爬虫环境 - 模拟真实大型网站的反爬虫系统
包括：AI行为检测、设备指纹、TLS指纹、JS挑战、蜜罐陷阱等
"""
import numpy as np
import gymnasium as gym
from gymnasium import spaces
import random
from collections import deque, defaultdict
import hashlib
import time


class HellModeAntiSpiderEnvironment(gym.Env):
    """地狱级反爬虫环境 - 修复和优化版本"""
    
    def __init__(self, config):
        """初始化环境"""
        super().__init__()
        
        # 配置参数
        if hasattr(config, '__dict__'):
            self.ip_pool_size = getattr(config, 'ip_pool_size', 50)
            self.max_requests = getattr(config, 'max_requests', 1000)
            self.ua_pool_size = getattr(config, 'ua_pool_size', 20)
        else:
            self.ip_pool_size = config.get('ip_pool_size', 50)
            self.max_requests = config.get('max_requests', 1000)
            self.ua_pool_size = config.get('ua_pool_size', 20)
        
        self.config = config
        
        # === 反爬虫检测参数（强化版）===
        # 1. 频率检测（多时间窗口）
        self.freq_windows = [10, 60, 300, 3600]  # 10秒、1分钟、5分钟、1小时
        self.freq_thresholds = [2, 8, 30, 80]  # 降低阈值，更严格
        self.freq_weights = [0.4, 0.3, 0.2, 0.1]  # 权重
        
        # 2. 行为分析
        self.min_interval = 0.5  # 最小间隔提高到0.5s
        self.max_safe_interval = 10.0  # 最大安全间隔
        self.behavior_window = 30  # 行为窗口
        
        # 3. 设备指纹系统
        self.fingerprint_db = {}  # 设备指纹数据库
        self.fingerprint_mismatch_threshold = 0.25  # 降低阈值，更敏感
        
        # 4. TLS指纹
        self.tls_fingerprint_db = {}
        
        # 5. AI行为模型（检测机器行为）
        self.ai_detector_threshold = 0.6  # 降低阈值
        self.human_behavior_variance = 0.3  # 人类行为随机性
        
        # 6. JS挑战系统
        self.js_challenge_prob = 0.20  # 提高到20%
        self.js_solve_success_rate = 0.5  # 降低解决率
        self.js_solve_time = 2.0  # JS解决时间
        
        # 7. Cookie追踪
        self.cookie_db = {}
        self.cookie_lifetime = 3600  # Cookie有效期
        
        # 8. 蜜罐系统
        self.honeypot_urls = set(range(15))  # 增加到15个蜜罐URL
        self.honeypot_penalty = -25  # 加重惩罚
        
        # 9. IP信誉数据库（全局）
        self.global_ip_reputation = {}
        
        # 10. CDN边缘节点检测
        self.cdn_node_tracking = defaultdict(list)
        
        # 11. 时间窗口限流
        self.burst_window = 5  # 突发检测窗口
        self.burst_threshold = 4  # 降低突发阈值
        
        # 12. 协议异常检测
        self.protocol_errors = defaultdict(int)
        
        # === 新增：地狱级特定参数 ===
        self.cumulative_risk_decay = 0.98  # 累积风险衰减慢
        self.ban_duration_multiplier = 1.5  # 封禁时长倍数
        self.reputation_recovery_rate = 0.005  # 信誉恢复慢
        
        # 环境状态变量
        self.current_step = 0
        self.current_ip = 0
        self.current_ua = 0
        self.current_cookie = None
        self.device_fingerprint = None
        self.tls_fingerprint = None
        
        self.request_count = 0
        self.ban_count = 0
        self.success_count = 0
        self.captcha_count = 0
        self.timeout_count = 0
        self.js_challenge_count = 0
        self.honeypot_hit_count = 0
        self.fingerprint_mismatch_count = 0
        
        # 时间戳（模拟）
        self.virtual_time = 0.0
        self.last_request_time = 0.0
        self.session_start_time = 0.0
        
        # IP状态追踪（增强版）
        self.ip_states = {}
        self.ua_states = {}
        
        # 请求历史（用于AI检测）
        self.request_history = deque(maxlen=self.behavior_window)
        self.interval_history = deque(maxlen=self.behavior_window)
        self.success_pattern = deque(maxlen=20)
        
        # 每个IP的请求时间戳（多时间窗口）
        self.ip_request_times = defaultdict(lambda: deque(maxlen=200))
        
        # 会话历史
        self.session_history = []
        
        # 观察空间 [18维] - 更多特征
        self.observation_space = spaces.Box(
            low=0.0,
            high=1.0,
            shape=(18,),
            dtype=np.float32
        )
        
        # 动作空间 [12个动作] - 更多策略选项
        self.action_space = spaces.Discrete(12)
        
        # 初始化
        self.reset()
    
    def reset(self, seed=None, options=None):
        """重置环境"""
        super().reset(seed=seed)
        
        # 重置计数器
        self.current_step = 0
        self.current_ip = random.randint(0, self.ip_pool_size - 1)
        self.current_ua = random.randint(0, self.ua_pool_size - 1)
        self.request_count = 0
        self.ban_count = 0
        self.success_count = 0
        self.captcha_count = 0
        self.timeout_count = 0
        self.js_challenge_count = 0
        self.honeypot_hit_count = 0
        self.fingerprint_mismatch_count = 0
        
        # 重置时间
        self.virtual_time = 0.0
        self.last_request_time = 0.0
        self.session_start_time = 0.0
        
        # 生成初始指纹
        self.device_fingerprint = self._generate_device_fingerprint()
        self.tls_fingerprint = self._generate_tls_fingerprint()
        self.current_cookie = self._generate_cookie()
        
        # 重置IP状态（更详细）
        self.ip_states = {}
        for i in range(self.ip_pool_size):
            # 地狱级：初始信誉更低且不均匀
            base_reputation = random.uniform(0.3, 0.7)
            
            self.ip_states[i] = {
                'reputation': base_reputation,
                'request_count': 0,
                'ban_count': 0,
                'last_ban_time': -999,
                'consecutive_fails': 0,
                'consecutive_success': 0,
                'total_requests': 0,
                'is_banned': False,
                'ban_until': 0.0,
                'ban_level': 0,
                'captcha_count': 0,
                'js_challenge_count': 0,
                'honeypot_hits': 0,
                'fingerprint_mismatches': 0,
                'last_activity': 0.0,
                'suspicious_score': random.uniform(0.0, 0.3),  # 初始可疑度
                'ai_detection_score': 0.0,
                'cumulative_risk': 0.2,  # 新增：累积风险基线
            }
        
        # 重置UA状态
        self.ua_states = {}
        for i in range(self.ua_pool_size):
            self.ua_states[i] = {
                'age': 0,
                'request_count': 0,
                'suspicious': False,
                'fingerprint': self._generate_ua_fingerprint(i)
            }
        
        # 清空历史
        self.request_history.clear()
        self.interval_history.clear()
        self.success_pattern.clear()
        self.ip_request_times.clear()
        self.session_history.clear()
        
        # 全局黑名单IP（模拟真实场景）- 地狱级更多
        num_blacklisted = int(self.ip_pool_size * 0.15)  # 15%被黑名单
        blacklisted_ips = random.sample(range(self.ip_pool_size), num_blacklisted)
        for ip_id in blacklisted_ips:
            self.ip_states[ip_id]['reputation'] = 0.05
            self.ip_states[ip_id]['suspicious_score'] = 0.9
            self.ip_states[ip_id]['cumulative_risk'] = 0.6
        
        observation = self._get_observation()
        info = self._get_info()
        
        return observation, info
    
    def _generate_device_fingerprint(self):
        """生成设备指纹"""
        fingerprint = {
            'screen_resolution': random.choice(['1920x1080', '1366x768', '2560x1440']),
            'timezone': random.choice([-8, -5, 0, 8]),
            'language': random.choice(['en-US', 'zh-CN', 'ja-JP']),
            'platform': random.choice(['Win32', 'MacIntel', 'Linux x86_64']),
            'plugins': random.randint(0, 10),
            'canvas_hash': hashlib.md5(str(random.random()).encode()).hexdigest()[:8],
            'webgl_vendor': random.choice(['NVIDIA', 'AMD', 'Intel']),
        }
        return fingerprint
    
    def _generate_tls_fingerprint(self):
        """生成TLS指纹"""
        return hashlib.md5(str(random.random()).encode()).hexdigest()[:16]
    
    def _generate_ua_fingerprint(self, ua_id):
        """生成UA指纹"""
        return hashlib.md5(f"ua_{ua_id}".encode()).hexdigest()[:12]
    
    def _generate_cookie(self):
        """生成Cookie"""
        return {
            'session_id': hashlib.md5(str(random.random()).encode()).hexdigest(),
            'created_at': self.virtual_time,
            'valid': True
        }
    
    def _get_observation(self):
        """获取当前观察（18维）"""
        ip_state = self.ip_states[self.current_ip]
        ua_state = self.ua_states[self.current_ua]
        
        # 1. IP信誉
        ip_reputation = ip_state['reputation']
        
        # 2. UA年龄
        ua_age_norm = min(1.0, ua_state['age'] / 100.0)
        
        # 3-6. 多时间窗口频率
        freq_features = []
        for window in self.freq_windows:
            freq = self._get_frequency_in_window(window)
            freq_features.append(min(1.0, freq * 2))  # 归一化
        
        # 7. 平均间隔
        avg_interval = np.mean(list(self.interval_history)) if len(self.interval_history) > 0 else 5.0
        avg_interval_norm = min(1.0, avg_interval / 20.0)
        
        # 8. 间隔方差（规律性）
        interval_variance = np.std(list(self.interval_history)) if len(self.interval_history) > 2 else 1.0
        variance_norm = min(1.0, interval_variance / 10.0)
        
        # 9. AI检测分数
        ai_score = ip_state['ai_detection_score']
        
        # 10. 连续成功率
        consecutive_success = min(1.0, ip_state['consecutive_success'] / 10.0)
        
        # 11. 连续失败数
        consecutive_fails = min(1.0, ip_state['consecutive_fails'] / 5.0)
        
        # 12. 验证码/JS挑战率
        challenge_rate = (self.captcha_count + self.js_challenge_count) / max(1, self.request_count)
        
        # 13. IP使用率
        ip_usage = sum(1 for s in self.ip_states.values() if s['total_requests'] > 0) / self.ip_pool_size
        
        # 14. 时间进度
        time_progress = self.current_step / self.max_requests
        
        # 15. 总成功率
        success_rate = self.success_count / max(1, self.request_count)
        
        # 16. 封禁率
        ban_rate = self.ban_count / max(1, self.request_count)
        
        # 17. 蜜罐命中率
        honeypot_rate = self.honeypot_hit_count / max(1, self.request_count)
        
        # 18. 综合风险评分
        risk_score = self._calculate_comprehensive_risk()
        
        observation = np.array([
            ip_reputation,
            ua_age_norm,
            freq_features[0],
            freq_features[1],
            freq_features[2],
            freq_features[3],
            avg_interval_norm,
            variance_norm,
            ai_score,
            consecutive_success,
            consecutive_fails,
            challenge_rate,
            ip_usage,
            time_progress,
            success_rate,
            ban_rate,
            honeypot_rate,
            risk_score
        ], dtype=np.float32)
        
        return observation
    
    def _get_info(self):
        """获取额外信息"""
        return {
            'current_step': self.current_step,
            'current_ip': self.current_ip,
            'current_ua': self.current_ua,
            'request_count': self.request_count,
            'success_count': self.success_count,
            'ban_count': self.ban_count,
            'captcha_count': self.captcha_count,
            'js_challenge_count': self.js_challenge_count,
            'timeout_count': self.timeout_count,
            'honeypot_hit_count': self.honeypot_hit_count,
            'fingerprint_mismatch_count': self.fingerprint_mismatch_count,
            'success_rate': self.success_count / max(1, self.request_count),
            'risk_score': self._calculate_comprehensive_risk(),
            'ip_reputation': self.ip_states[self.current_ip]['reputation'],
            'ai_detection_score': self.ip_states[self.current_ip]['ai_detection_score'],
            'cumulative_risk': self.ip_states[self.current_ip]['cumulative_risk']
        }
    
    def step(self, action):
        """执行动作（优化版）"""
        self.current_step += 1
        reward = 0
        terminated = False
        truncated = False
        
        # 解析动作
        interval, change_ip, change_ua, reset_session = self._parse_action(action)
        
        # 更新虚拟时间
        self.virtual_time += interval
        
        # 换IP/UA成本
        if change_ip:
            old_ip = self.current_ip
            self.current_ip = self._select_new_ip()
            reward -= 0.5  # 增加换IP成本
            
            # 换IP后指纹可能不匹配概率提高
            if random.random() < 0.4:
                self.fingerprint_mismatch_count += 1
                reward -= 1.0
        
        if change_ua:
            self.current_ua = self._select_new_ua()
            reward -= 0.2
        
        if reset_session:
            self.device_fingerprint = self._generate_device_fingerprint()
            self.tls_fingerprint = self._generate_tls_fingerprint()
            self.current_cookie = self._generate_cookie()
            self.session_start_time = self.virtual_time
            reward -= 0.8  # 增加重置成本
        
        # 更新UA年龄
        self.ua_states[self.current_ua]['age'] += 1
        
        # 执行请求
        request_result = self._make_request(interval)
        
        # === 修复：更精细的奖励设计 ===
        if request_result == 'success':
            # 基础成功奖励
            base_reward = 1.0
            
            # 效率奖励（快速成功）
            if interval < 2.0:
                base_reward += 0.5
            elif interval < 5.0:
                base_reward += 0.2
            elif interval > 15.0:
                base_reward -= 0.3  # 太慢效率低
            
            # 连续成功奖励
            if self.ip_states[self.current_ip]['consecutive_success'] > 3:
                base_reward += 0.3
            
            reward += base_reward
            self.success_count += 1
            self.ip_states[self.current_ip]['consecutive_fails'] = 0
            self.ip_states[self.current_ip]['consecutive_success'] += 1
            self.success_pattern.append(1)
        
        elif request_result == 'banned':
            # 封禁惩罚（更重）
            ban_penalty = -12.0
            
            # 高级封禁更严重
            ban_level = self.ip_states[self.current_ip]['ban_level']
            if ban_level > 2:
                ban_penalty -= 8.0 * (ban_level - 2)
            
            # 短时间内多次封禁额外惩罚
            if self.ban_count > 0 and (self.virtual_time - self.ip_states[self.current_ip]['last_ban_time']) < 100:
                ban_penalty -= 5.0
            
            reward += ban_penalty
            self.ban_count += 1
            self.ip_states[self.current_ip]['consecutive_fails'] += 1
            self.ip_states[self.current_ip]['consecutive_success'] = 0
            self.ip_states[self.current_ip]['ban_level'] += 1
            self.ip_states[self.current_ip]['last_ban_time'] = self.virtual_time
            self.success_pattern.append(0)
        
        elif request_result == 'captcha':
            reward -= 3.0
            self.captcha_count += 1
            self.ip_states[self.current_ip]['captcha_count'] += 1
            
            # 尝试解决验证码（成功率更低）
            if random.random() < 0.6:
                reward += 0.5
                self.success_count += 1
                self.success_pattern.append(1)
            else:
                reward -= 2.0
                self.success_pattern.append(0)
        
        elif request_result == 'js_challenge':
            reward -= 4.0
            self.js_challenge_count += 1
            self.ip_states[self.current_ip]['js_challenge_count'] += 1
            
            if random.random() < self.js_solve_success_rate:
                reward += 0.3
                self.success_count += 1
                self.success_pattern.append(1)
            else:
                reward -= 2.5
                self.success_pattern.append(0)
        
        elif request_result == 'honeypot':
            reward += self.honeypot_penalty
            self.honeypot_hit_count += 1
            self.ip_states[self.current_ip]['honeypot_hits'] += 1
            self.success_pattern.append(0)
        
        elif request_result == 'timeout':
            reward -= 2.0
            self.timeout_count += 1
            self.ip_states[self.current_ip]['consecutive_fails'] += 1
            self.success_pattern.append(0)
        
        elif request_result == 'rate_limited':
            reward -= 5.0
            self.ip_states[self.current_ip]['consecutive_fails'] += 1
            self.success_pattern.append(0)
        
        elif request_result == 'fingerprint_mismatch':
            reward -= 8.0
            self.fingerprint_mismatch_count += 1
            self.ip_states[self.current_ip]['fingerprint_mismatches'] += 1
            self.success_pattern.append(0)
        
        # 更新请求计数
        self.request_count += 1
        self.last_request_time = self.virtual_time
        
        # 记录请求历史
        self.request_history.append({
            'ip': self.current_ip,
            'ua': self.current_ua,
            'interval': interval,
            'result': request_result,
            'time': self.virtual_time
        })
        self.interval_history.append(interval)
        
        # 更新AI检测分数
        self._update_ai_detection_score()
        
        # 检查终止条件（更严格）
        if self.current_step >= self.max_requests:
            truncated = True
        
        # 如果太多IP被封禁
        banned_ips = sum(1 for s in self.ip_states.values() if s['is_banned'])
        if banned_ips > self.ip_pool_size * 0.5:  # 降低到50%
            terminated = True
            reward -= 25.0
        
        # 如果成功率太低（地狱级：更严格）
        if self.request_count > 50:
            current_success_rate = self.success_count / self.request_count
            if current_success_rate < 0.03:  # 低于3%
                terminated = True
                reward -= 20.0
        
        # 如果风险评分太高
        if self._calculate_comprehensive_risk() > 0.92:
            terminated = True
            reward -= 15.0
        
        # 如果封禁次数太多
        if self.ban_count > 15:
            terminated = True
            reward -= 10.0
        
        observation = self._get_observation()
        info = self._get_info()
        
        return observation, reward, terminated, truncated, info
    
    def _parse_action(self, action):
        """解析动作 -> (interval, change_ip, change_ua, reset_session)"""
        action_map = {
            0: (0.5, False, False, False),   # 极速（提高最小间隔）
            1: (random.uniform(0.8, 1.5), False, False, False),  # 快速
            2: (random.uniform(1.5, 4.0), False, False, False),  # 正常
            3: (random.uniform(4.0, 10.0), False, False, False),  # 慢速
            4: (2.0, True, False, False),    # 换IP（增加间隔）
            5: (1.5, False, True, False),    # 换UA
            6: (3.0, True, True, False),     # 全换（增加间隔）
            7: (12.0, False, False, False),  # 冷却（增加等待）
            8: (25.0, True, False, False),   # 长等待+换IP
            9: (70.0, True, True, True),     # 紧急避险（增加等待）
            10: (random.uniform(4.0, 18.0), False, False, False),  # 模拟人类
            11: (6.0, False, False, True),   # 重置会话
        }
        return action_map.get(action, (2.0, False, False, False))
    
    def _select_new_ip(self):
        """智能选择新IP（优化版）"""
        available_ips = []
        for ip_id, state in self.ip_states.items():
            if ip_id == self.current_ip:
                continue
            
            if state['is_banned']:
                continue
            
            # 计算权重（更复杂的评分）
            weight = state['reputation'] ** 1.5  # 信誉的影响更大
            weight *= (1.0 - state['suspicious_score']) ** 1.2
            weight *= (1.0 - min(1.0, state['total_requests'] / 150.0))
            weight *= (1.0 - state['ai_detection_score']) ** 1.3
            weight *= (1.0 - min(1.0, state['cumulative_risk']))
            
            # 休息过的IP权重更高
            idle_time = self.virtual_time - state['last_activity']
            if idle_time > 150:
                weight *= 2.0
            elif idle_time > 50:
                weight *= 1.3
            
            # 没有封禁历史的加成
            if state['ban_count'] == 0:
                weight *= 1.5
            
            # 蜜罐和指纹问题的惩罚
            if state['honeypot_hits'] > 0:
                weight *= 0.3
            if state['fingerprint_mismatches'] > 0:
                weight *= 0.5
            
            if weight > 0.05:
                available_ips.append((ip_id, weight))
        
        if not available_ips:
            # 找未封禁的
            available_ips = [(ip_id, 0.05) for ip_id, state in self.ip_states.items() 
                           if not state['is_banned'] and ip_id != self.current_ip]
        
        if not available_ips:
            return self.current_ip
        
        ip_ids, weights = zip(*available_ips)
        weights = np.array(weights)
        weights = weights / weights.sum()
        
        return np.random.choice(ip_ids, p=weights)
    
    def _select_new_ua(self):
        """智能选择新UA"""
        available_uas = []
        for ua_id, state in self.ua_states.items():
            if ua_id == self.current_ua:
                continue
            
            weight = 1.0 / (1.0 + state['request_count'] / 15.0)
            if not state['suspicious']:
                weight *= 2.5
            
            # 新UA权重更高
            if state['age'] < 10:
                weight *= 1.5
            
            available_uas.append((ua_id, weight))
        
        if not available_uas:
            return random.randint(0, self.ua_pool_size - 1)
        
        ua_ids, weights = zip(*available_uas)
        weights = np.array(weights)
        weights = weights / weights.sum()
        
        return np.random.choice(ua_ids, p=weights)
    
    def _make_request(self, interval):
        """
        模拟发送请求（地狱级检测 - 强化版）
        
        Returns:
            'success', 'banned', 'captcha', 'js_challenge', 
            'honeypot', 'timeout', 'rate_limited', 'fingerprint_mismatch'
        """
        ip_state = self.ip_states[self.current_ip]
        
        # 更新活动时间
        ip_state['last_activity'] = self.virtual_time
        
        # 1. 检查IP是否被封禁
        if ip_state['is_banned']:
            if self.virtual_time < ip_state['ban_until']:
                return 'banned'
            else:
                # 解封，但信誉和累积风险大幅下降
                ip_state['is_banned'] = False
                ip_state['reputation'] = max(0.05, ip_state['reputation'] * 0.3)
                ip_state['suspicious_score'] = min(1.0, ip_state['suspicious_score'] + 0.4)
                ip_state['cumulative_risk'] = min(1.0, ip_state['cumulative_risk'] + 0.2)
        
        # 2. 记录请求时间
        self.ip_request_times[self.current_ip].append(self.virtual_time)
        ip_state['total_requests'] += 1
        self.ua_states[self.current_ua]['request_count'] += 1
        
        # 3. Cookie验证（更严格）
        if self.current_cookie is None or not self.current_cookie['valid']:
            return 'banned'
        
        if self.virtual_time - self.current_cookie['created_at'] > self.cookie_lifetime:
            self.current_cookie['valid'] = False
            return 'banned'
        
        # 4. 设备指纹验证
        fingerprint_risk = self._check_fingerprint_consistency()
        if fingerprint_risk > self.fingerprint_mismatch_threshold:
            return 'fingerprint_mismatch'
        
        # 5. 蜜罐检测（概率提高）
        if random.random() < 0.08:  # 提高到8%
            target_url = random.randint(0, 29)
            if target_url in self.honeypot_urls:
                ip_state['honeypot_hits'] += 1
                ip_state['reputation'] *= 0.2
                ip_state['suspicious_score'] = 1.0
                ip_state['cumulative_risk'] = min(1.0, ip_state['cumulative_risk'] + 0.3)
                return 'honeypot'
        
        # 6. 计算综合检测分数（强化版）
        detection_score = 0.0
        
        # 6.1 多时间窗口频率检测
        for i, window in enumerate(self.freq_windows):
            freq = self._get_frequency_in_window(window)
            threshold = self.freq_thresholds[i] / window
            if freq > threshold:
                overage = min(2.0, freq / threshold)
                detection_score += self.freq_weights[i] * (overage - 1.0) * 1.5  # 加重权重
        
        # 6.2 间隔检测（更严格）
        if interval < self.min_interval:
            detection_score += 0.7  # 提高惩罚
        elif interval < 1.0:
            detection_score += 0.3
        
        # 6.3 突发检测（强化）
        burst_count = sum(1 for t in self.ip_request_times[self.current_ip]
                         if self.virtual_time - t <= self.burst_window)
        if burst_count > self.burst_threshold:
            burst_severity = min(2.0, burst_count / self.burst_threshold)
            detection_score += 0.8 * burst_severity
        
        # 6.4 AI行为检测（权重提高）
        ai_score = ip_state['ai_detection_score']
        detection_score += ai_score * 1.0  # 从0.8提高到1.0
        
        # 6.5 历史记录（更严格）
        if ip_state['ban_count'] > 0:
            detection_score += 0.3 * min(1.5, ip_state['ban_count'] / 2.0)
        
        if ip_state['captcha_count'] > 2:
            detection_score += 0.4
        
        if ip_state['honeypot_hits'] > 0:
            detection_score += 0.8 * ip_state['honeypot_hits']
        
        if ip_state['fingerprint_mismatches'] > 0:
            detection_score += 0.6 * ip_state['fingerprint_mismatches']
        
        # 6.6 信誉系统（影响加大）
        if ip_state['reputation'] < 0.3:
            detection_score += 0.7
        elif ip_state['reputation'] < 0.5:
            detection_score += 0.4
        
        if ip_state['suspicious_score'] > 0.6:
            detection_score += 0.6
        
        # 6.7 累积风险（新增）
        detection_score += ip_state['cumulative_risk'] * 0.5
        
        # 6.8 指纹风险
        detection_score += fingerprint_risk * 0.4
        
        # 6.9 连续失败（权重提高）
        if ip_state['consecutive_fails'] > 2:
            detection_score += 0.5 * min(1.0, ip_state['consecutive_fails'] / 4.0)
        
        # 限制在0-1之间
        detection_score = min(1.0, detection_score)
        
        # 7. 根据检测分数决定结果（更严格的阈值）
        
        # 7.1 极高分 -> 直接封禁
        if detection_score > 0.75 or ip_state['ban_level'] >= 3:
            ip_state['is_banned'] = True
            ban_duration = random.uniform(300, 800) * (1 + ip_state['ban_level']) * self.ban_duration_multiplier
            ip_state['ban_until'] = self.virtual_time + ban_duration
            ip_state['ban_count'] += 1
            ip_state['reputation'] *= 0.2
            ip_state['suspicious_score'] = min(1.0, ip_state['suspicious_score'] + 0.5)
            ip_state['cumulative_risk'] = min(1.0, ip_state['cumulative_risk'] + 0.3)
            return 'banned'
        
        # 7.2 高分 -> JS挑战
        if detection_score > 0.55:
            js_prob = (detection_score - 0.55) * 4
            if random.random() < js_prob:
                ip_state['js_challenge_count'] += 1
                ip_state['reputation'] *= 0.8
                ip_state['cumulative_risk'] = min(1.0, ip_state['cumulative_risk'] + 0.1)
                return 'js_challenge'
        
        # 7.3 中高分 -> 验证码
        if detection_score > 0.35:
            captcha_prob = self.js_challenge_prob + (detection_score - 0.35) * 2.0
            if random.random() < captcha_prob:
                ip_state['captcha_count'] += 1
                ip_state['reputation'] *= 0.85
                ip_state['cumulative_risk'] = min(1.0, ip_state['cumulative_risk'] + 0.08)
                return 'captcha'
        
        # 7.4 中等分 -> 限流
        if detection_score > 0.25:
            rate_limit_prob = (detection_score - 0.25) * 2.5
            if random.random() < rate_limit_prob:
                ip_state['reputation'] *= 0.88
                ip_state['suspicious_score'] = min(1.0, ip_state['suspicious_score'] + 0.15)
                ip_state['cumulative_risk'] = min(1.0, ip_state['cumulative_risk'] + 0.05)
                return 'rate_limited'
        
        # 8. 网络超时（概率提高）
        if random.random() < 0.10:  # 10%超时率
            return 'timeout'
        
        # 9. 成功！但信誉恢复慢
        ip_state['reputation'] = min(1.0, ip_state['reputation'] + self.reputation_recovery_rate)
        ip_state['suspicious_score'] = max(0.0, ip_state['suspicious_score'] * 0.96)
        ip_state['cumulative_risk'] = max(0.1, ip_state['cumulative_risk'] * self.cumulative_risk_decay)
        
        return 'success'
    
    def _get_frequency_in_window(self, window):
        """获取指定时间窗口内的请求频率"""
        if self.current_ip not in self.ip_request_times:
            return 0.0
        
        recent_requests = [t for t in self.ip_request_times[self.current_ip] 
                          if self.virtual_time - t <= window]
        
        return len(recent_requests) / max(1.0, window)
    
    def _check_fingerprint_consistency(self):
        """检查指纹一致性（返回风险分数）"""
        risk = 0.0
        
        ip_fingerprint_key = f"ip_{self.current_ip}"
        
        if ip_fingerprint_key in self.fingerprint_db:
            stored_fp = self.fingerprint_db[ip_fingerprint_key]
            
            # 检查各项是否匹配（权重调整）
            if stored_fp['screen_resolution'] != self.device_fingerprint['screen_resolution']:
                risk += 0.35
            if stored_fp['timezone'] != self.device_fingerprint['timezone']:
                risk += 0.25
            if stored_fp['platform'] != self.device_fingerprint['platform']:
                risk += 0.50
            if stored_fp['canvas_hash'] != self.device_fingerprint['canvas_hash']:
                risk += 0.40
            if stored_fp['webgl_vendor'] != self.device_fingerprint['webgl_vendor']:
                risk += 0.20
        else:
            # 首次记录指纹
            self.fingerprint_db[ip_fingerprint_key] = self.device_fingerprint.copy()
        
        return min(1.0, risk)
    
    def _update_ai_detection_score(self):
        """更新AI行为检测分数（强化版）"""
        ip_state = self.ip_states[self.current_ip]
        
        if len(self.interval_history) < 5:
            return
        
        intervals = list(self.interval_history)
        
        # 1. 规律性检测（更敏感）
        std = np.std(intervals)
        mean = np.mean(intervals)
        if mean > 0:
            cv = std / mean
            # 变异系数越小越规律（机器行为）
            regularity_score = 1.0 / (1.0 + cv * 2)  # 降低分母，更敏感
        else:
            regularity_score = 1.0
        
        # 2. 成功模式检测
        if len(self.success_pattern) >= 10:
            success_pattern_list = list(self.success_pattern)
            pattern_score = 0.0
            
            # 检查连续相同结果
            for i in range(len(success_pattern_list) - 2):
                if success_pattern_list[i] == success_pattern_list[i+1] == success_pattern_list[i+2]:
                    pattern_score += 0.15
            
            pattern_score = min(1.0, pattern_score)
        else:
            pattern_score = 0.0
        
        # 3. 请求时间分布检测
        if len(self.request_history) >= 10:
            hours = [(req['time'] % 86400) // 3600 for req in self.request_history]
            unique_hours = len(set(hours))
            time_diversity = unique_hours / 24.0
            time_score = 1.0 - time_diversity
        else:
            time_score = 0.0
        
        # 4. 间隔分布检测（新增）
        if len(intervals) >= 10:
            # 检查是否有明显的间隔模式（如总是3秒、5秒等）
            rounded_intervals = [round(i) for i in intervals]
            unique_intervals = len(set(rounded_intervals))
            if unique_intervals < 3:  # 只有少数几种间隔
                interval_pattern_score = 0.8
            else:
                interval_pattern_score = max(0.0, 1.0 - unique_intervals / 10.0)
        else:
            interval_pattern_score = 0.0
        
        # 5. 综合AI检测分数（权重调整）
        ai_score = (regularity_score * 0.35 + 
                   pattern_score * 0.25 + 
                   time_score * 0.20 +
                   interval_pattern_score * 0.20)
        
        # 指数移动平均更新（保留更多历史）
        ip_state['ai_detection_score'] = (ip_state['ai_detection_score'] * 0.85 + 
                                          ai_score * 0.15)
    
    def _calculate_comprehensive_risk(self):
        """计算综合风险评分（优化版）"""
        ip_state = self.ip_states[self.current_ip]
        
        risk = 0.0
        
        # 各因素权重（重新平衡）
        risk += (1.0 - ip_state['reputation']) * 0.22
        risk += ip_state['suspicious_score'] * 0.18
        risk += ip_state['ai_detection_score'] * 0.18
        risk += min(1.0, ip_state['ban_count'] / 2.5) * 0.15
        risk += min(1.0, ip_state['honeypot_hits'] / 1.5) * 0.12
        risk += min(1.0, ip_state['fingerprint_mismatches'] / 2.5) * 0.10
        risk += ip_state['cumulative_risk'] * 0.05
        
        return min(1.0, risk)
    
    def render(self):
        """渲染环境状态"""
        print(f"\n{'='*80}")
        print(f"步数: {self.current_step}/{self.max_requests} | 虚拟时间: {self.virtual_time:.1f}s")
        print(f"当前IP: {self.current_ip} (信誉: {self.ip_states[self.current_ip]['reputation']:.2f}, "
              f"AI分数: {self.ip_states[self.current_ip]['ai_detection_score']:.2f}, "
              f"累积风险: {self.ip_states[self.current_ip]['cumulative_risk']:.2f})")
        print(f"请求: {self.request_count} | 成功: {self.success_count} "
              f"({self.success_count/max(1,self.request_count)*100:.1f}%)")
        print(f"封禁: {self.ban_count} | 验证码: {self.captcha_count} | "
              f"JS挑战: {self.js_challenge_count}")
        print(f"蜜罐: {self.honeypot_hit_count} | 指纹失配: {self.fingerprint_mismatch_count}")
        print(f"综合风险: {self._calculate_comprehensive_risk():.2f}")
        
        banned = sum(1 for s in self.ip_states.values() if s['is_banned'])
        print(f"IP池: {banned}/{self.ip_pool_size} 被封禁")
        print(f"{'='*80}\n")
    
    def close(self):
        """关闭环境"""
        pass


def make_hell_mode_env(config=None):
    """创建地狱级环境"""
    if config is None:
        config = {
            'ip_pool_size': 50,
            'max_requests': 1000,
            'ua_pool_size': 20
        }
    
    return HellModeAntiSpiderEnvironment(config)