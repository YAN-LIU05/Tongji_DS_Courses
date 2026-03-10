"""
快速检查脚本 - 分析你的验证码文件
"""
import os
from collections import Counter

# 检查训练数据
train_dir = './data/train'

if not os.path.exists(train_dir):
    print(f"错误: {train_dir} 不存在，请先运行 preprocess.py")
    exit()

# 获取所有文件
files = [f for f in os.listdir(train_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]

print("="*60)
print(f"检查 {train_dir}")
print("="*60)
print(f"总文件数: {len(files)}\n")

# 分析前100个文件
sample_files = files[:100]

print("前20个文件名:")
for i, f in enumerate(sample_files[:20], 1):
    label = os.path.splitext(f)[0]
    print(f"  {i:2d}. {f:30s} -> 标签: '{label}' (长度: {len(label)})")

# 统计所有字符
all_labels = [os.path.splitext(f)[0] for f in sample_files]
all_chars = ''.join(all_labels)
char_counter = Counter(all_chars)

print(f"\n字符统计 (前100个文件):")
print(f"  唯一字符数: {len(char_counter)}")
print(f"  字符列表: {sorted(char_counter.keys())}")

# 按类别分组
digits = [c for c in char_counter.keys() if c.isdigit()]
lower = [c for c in char_counter.keys() if c.islower()]
upper = [c for c in char_counter.keys() if c.isupper()]
others = [c for c in char_counter.keys() if not (c.isdigit() or c.isalpha())]

print(f"\n字符分类:")
print(f"  数字 ({len(digits)}): {sorted(digits)}")
print(f"  小写字母 ({len(lower)}): {sorted(lower)}")
print(f"  大写字母 ({len(upper)}): {sorted(upper)}")
if others:
    print(f"  其他字符 ({len(others)}): {others}")

# 统计标签长度
label_lengths = Counter([len(os.path.splitext(f)[0]) for f in sample_files])
print(f"\n标签长度分布:")
for length, count in sorted(label_lengths.items()):
    print(f"  长度 {length}: {count} 个")

# 生成建议的字符集
suggested_charset = ''.join(sorted(set(all_chars)))
print(f"\n建议的字符集 (CHARSET):")
print(f"  {suggested_charset}")
print(f"  总共 {len(suggested_charset)} 个字符")

# 检查是否有特殊字符
if others:
    print(f"\n⚠️ 警告: 发现特殊字符: {others}")
    print("  这些字符可能会导致问题，请检查文件名是否正确")