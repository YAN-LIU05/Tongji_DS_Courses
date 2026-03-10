import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import numpy as np

# 忽略警告信息
warnings.filterwarnings('ignore')

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False     # 用来正常显示负号

# 读取三个Excel文件
element_df = pd.read_excel('element.xlsx')
age_df = pd.read_excel('age.xlsx')
strength_df = pd.read_excel('strength.xlsx')

# 查看各数据集的基本信息
print("=" * 60)
print("元素配比数据 (element.xlsx) 基本信息：")
print(f"数据形状: {element_df.shape}")
print(f"列名: {element_df.columns.tolist()}")
print("\n前5行数据：")
print(element_df.head())

print("\n" + "=" * 60)
print("养护时间数据 (age.xlsx) 基本信息：")
print(f"数据形状: {age_df.shape}")
print(f"列名: {age_df.columns.tolist()}")
print("\n前5行数据：")
print(age_df.head())

print("\n" + "=" * 60)
print("强度测试数据 (strength.xlsx) 基本信息：")
print(f"数据形状: {strength_df.shape}")
print(f"列名: {strength_df.columns.tolist()}")
print("\n前5行数据：")
print(strength_df.head())

# 检查各数据集的列名
print("重命名前的列名对比：")
print(f"Element列名: {element_df.columns.tolist()}")
print(f"Age列名: {age_df.columns.tolist()}")
print(f"Strength列名: {strength_df.columns.tolist()}")

# 模式对齐：重命名age_df和strength_df中的列名
age_df = age_df.rename(columns={'No.': 'number'})
strength_df = strength_df.rename(columns={'serial_number': 'number'})

print("\n" + "=" * 60)
print("重命名后的列名：")
print(f"Element列名: {element_df.columns.tolist()}")
print(f"Age列名: {age_df.columns.tolist()}")
print(f"Strength列名: {strength_df.columns.tolist()}")

# 验证重命名是否成功
print("\n重命名后的Age数据前5行：")
print(age_df.head())

# 第一步：合并element和age数据
# 使用inner join确保只保留三个表都有的记录
merged_df = pd.merge(element_df, age_df, on='number', how='inner')

print("=" * 60)
print("第一次合并 (Element + Age) 结果：")
print(f"合并后的数据形状: {merged_df.shape}")
print(f"合并后的列名: {merged_df.columns.tolist()}")
print("\n合并后前5行数据：")
print(merged_df.head())

# 第二步：将strength数据合并进来
final_df = pd.merge(merged_df, strength_df, on='number', how='inner')

print("\n" + "=" * 60)
print("最终合并 (Element + Age + Strength) 结果：")
print(f"最终数据形状: {final_df.shape}")
print(f"最终列数: {len(final_df.columns)}")
print(f"最终列名: {final_df.columns.tolist()}")

# 显示合并后的样本数据
print("\n最终合并后前10行数据：")
print(final_df.head(10))

# 检查缺失值
print("\n" + "=" * 60)
print("数据质量检查 - 缺失值统计：")
missing_counts = final_df.isnull().sum()
print(missing_counts[missing_counts > 0])  # 只显示有缺失值的列

if missing_counts.sum() == 0:
    print("所有列均无缺失值")
else:
    print(f"发现缺失值，总计: {missing_counts.sum()}")

# 检查重复记录
duplicate_count = final_df.duplicated(subset=['number']).sum()
print(f"\n重复记录检查：")
print(f"基于编号的重复记录数: {duplicate_count}")

if duplicate_count > 0:
    print("发现重复记录，需要处理")
    # 显示重复的记录
    duplicates = final_df[final_df.duplicated(subset=['number'], keep=False)]
    print(duplicates)
else:
    print("无重复记录")

# 删除可能存在的缺失值
original_count = len(final_df)
final_df = final_df.dropna()
cleaned_count = len(final_df)

print(f"\n数据清洗结果：")
print(f"原始记录数: {original_count}")
print(f"清洗后记录数: {cleaned_count}")
print(f"删除记录数: {original_count - cleaned_count}")

# 重新排列列的顺序，使数据更加清晰易读
columns_order = [
    'number', 
    'Cement (component 1)(kg in a m^3 mixture)',
    'Blast Furnace Slag (component 2)(kg in a m^3 mixture)',
    'Fly Ash (component 3)(kg in a m^3 mixture)',
    'Water  (component 4)(kg in a m^3 mixture)',
    'Superplasticizer (component 5)(kg in a m^3 mixture)',
    'Coarse Aggregate  (component 6)(kg in a m^3 mixture)',
    'Fine Aggregate (component 7)(kg in a m^3 mixture)',
    'Age (day)',
    'Concrete compressive strength(MPa, megapascals) '
]

final_df = final_df[columns_order]

print("\n" + "=" * 60)
print("列顺序调整完成，最终数据集前5行：")
print(final_df.head())

# 保存集成后的数据到Excel文件
output_filename = 'integrated_concrete_data.xlsx'
with pd.ExcelWriter(output_filename, engine='openpyxl') as writer:
    final_df.to_excel(writer, sheet_name='IntegratedData', index=False)

print(f"\n✓ 数据已成功保存到 '{output_filename}'")
print(f"  总记录数: {len(final_df)}")
print(f"  总属性数: {len(final_df.columns)}")


# 输出基本统计信息
print("\n" + "=" * 60)
print("=== 集成数据统计摘要 ===")
print(f"总记录数: {len(final_df)}")
print(f"总属性数: {len(final_df.columns)}")

print(f"\n数值属性的描述性统计：")
stats_summary = final_df.describe()
print(stats_summary)

# 保存统计摘要到Excel
stats_summary.to_excel('data_summary.xlsx')
print("\n✓ 统计摘要已保存到 'data_summary.xlsx'")

# 创建图形
plt.figure(figsize=(10, 6))

# 绘制散点图
plt.scatter(
    final_df['Cement (component 1)(kg in a m^3 mixture)'], 
    final_df['Concrete compressive strength(MPa, megapascals) '],
    alpha=0.6,           # 设置透明度
    edgecolors='k',      # 点的边缘颜色
    linewidth=0.5,       # 边缘线宽
    c='steelblue'        # 点的填充颜色
)

plt.xlabel('水泥含量 (kg/m^3)', fontsize=12)
plt.ylabel('抗压强度 (MPa)', fontsize=12)
plt.title('水泥含量与混凝土抗压强度的关系', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3, linestyle='--')
plt.tight_layout()

# 保存图片
plt.savefig('cement_vs_strength.png', dpi=300, bbox_inches='tight')
print("\n✓ 散点图已保存为 'cement_vs_strength.png'")
plt.show()

# 按龄期分组计算平均抗压强度
age_strength = final_df.groupby('Age (day)')['Concrete compressive strength(MPa, megapascals) '].mean().sort_index()

print("\n不同龄期的平均抗压强度：")
print(age_strength)

# 创建柱状图
plt.figure(figsize=(14, 6))
bars = plt.bar(
    age_strength.index, 
    age_strength.values, 
    color='steelblue',
    edgecolor='black',
    linewidth=0.7,
    alpha=0.8
)

# 在柱子上添加数值标签
for bar in bars:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2.,
        height,
        f'{height:.1f}',
        ha='center',
        va='bottom',
        fontsize=8
    )

plt.xlabel('养护龄期 (天)', fontsize=12)
plt.ylabel('平均抗压强度 (MPa)', fontsize=12)
plt.title('不同养护龄期的混凝土平均抗压强度', fontsize=14, fontweight='bold')
plt.grid(True, axis='y', alpha=0.3, linestyle='--')
plt.tight_layout()

# 保存图片
plt.savefig('age_vs_strength.png', dpi=300, bbox_inches='tight')
print("✓ 柱状图已保存为 'age_vs_strength.png'")
plt.show()

# 为了便于显示，创建副本并重命名列
correlation_df = final_df.copy()
correlation_df.columns = [
    '编号', '水泥', '矿渣', '粉煤灰', '水', 
    '减水剂', '粗骨料', '细骨料', '龄期', '抗压强度'
]

# 选择数值列计算相关性矩阵（排除编号列）
numeric_cols = correlation_df.columns[1:]
corr_matrix = correlation_df[numeric_cols].corr()

print("\n属性相关性矩阵：")
print(corr_matrix)

# 创建热力图
plt.figure(figsize=(12, 10))
sns.heatmap(
    corr_matrix, 
    annot=True,           # 在单元格中显示数值
    fmt='.2f',            # 数值格式保留两位小数
    cmap='coolwarm',      # 使用冷暖色调
    center=0,             # 以0为中心
    square=True,          # 单元格为正方形
    linewidths=0.5,       # 网格线宽度
    cbar_kws={'label': '相关系数'},
    vmin=-1,              # 最小值
    vmax=1                # 最大值
)

plt.title('混凝土各成分与性能属性相关性热力图', fontsize=14, fontweight='bold', pad=20)
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()

# 保存图片
plt.savefig('correlation_heatmap.png', dpi=300, bbox_inches='tight')
print("✓ 热力图已保存为 'correlation_heatmap.png'")
plt.show()

# 创建子图展示各成分的分布
fig, axes = plt.subplots(2, 4, figsize=(16, 8))
components = ['水泥', '矿渣', '粉煤灰', '水', '减水剂', '粗骨料', '细骨料', '抗压强度']

for idx, (ax, comp) in enumerate(zip(axes.flatten(), components)):
    # 绘制直方图
    n, bins, patches = ax.hist(
        correlation_df[comp], 
        bins=30, 
        color='skyblue', 
        edgecolor='black', 
        alpha=0.7
    )
    
    # 添加统计信息
    mean_val = correlation_df[comp].mean()
    median_val = correlation_df[comp].median()
    
    ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'均值: {mean_val:.1f}')
    ax.axvline(median_val, color='green', linestyle='--', linewidth=2, label=f'中位数: {median_val:.1f}')
    
    ax.set_xlabel(comp, fontsize=10)
    ax.set_ylabel('频数', fontsize=10)
    ax.set_title(f'{comp}分布', fontsize=11, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    ax.legend(fontsize=8)

plt.suptitle('混凝土各成分含量分布图', fontsize=14, fontweight='bold', y=1.00)
plt.tight_layout()

# 保存图片
plt.savefig('components_distribution.png', dpi=300, bbox_inches='tight')
print("✓ 分布图已保存为 'components_distribution.png'")
plt.show()

plt.figure(figsize=(12, 6))
ages_sorted = sorted(final_df['Age (day)'].unique())
data_by_age = [final_df[final_df['Age (day)'] == age]['Concrete compressive strength(MPa, megapascals) '].values for age in ages_sorted]
bp = plt.boxplot(data_by_age, labels=ages_sorted, patch_artist=True,
                 notch=True, showmeans=True,
                 boxprops=dict(facecolor='lightblue', alpha=0.7, edgecolor='black'),
                 whiskerprops=dict(color='black', linewidth=1.5),
                 capprops=dict(color='black', linewidth=1.5),
                 medianprops=dict(color='red', linewidth=2),
                 meanprops=dict(marker='D', markerfacecolor='orange', 
                               markeredgecolor='black', markersize=6),
                 flierprops=dict(marker='o', markerfacecolor='gray', 
                               markersize=5, alpha=0.5))
plt.xlabel('养护龄期 (天)', fontsize=12, fontweight='bold')
plt.ylabel('抗压强度 (MPa)', fontsize=12, fontweight='bold')
plt.title('不同养护龄期的强度分布箱线图', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3, axis='y', linestyle='--')
plt.tight_layout()
plt.savefig('age_strength_boxplot.png', dpi=300, bbox_inches='tight')
plt.close()
print("已保存: age_strength_boxplot.png")

# 配对散点图矩阵：多变量关系探索 
# 选择关键变量
key_vars = ['Cement (component 1)(kg in a m^3 mixture)', 'Water  (component 4)(kg in a m^3 mixture)', 'Age (day)', 'Concrete compressive strength(MPa, megapascals) ']
df_pair = final_df[key_vars].copy()
df_pair.columns = ['水泥', '水', '龄期', '强度']
# 创建龄期分组用于颜色编码
df_pair['龄期组'] = pd.cut(final_df['Age (day)'], bins=[0, 7, 28, 365], 
                          labels=['早期(≤7天)', '中期(8-28天)', '后期(>28天)'])
pairplot = sns.pairplot(df_pair, hue='龄期组', 
                        palette=['#FF6B6B', '#4ECDC4', '#45B7D1'],
                        diag_kind='kde', plot_kws={'alpha': 0.6, 's': 30},
                        corner=False)
pairplot.fig.suptitle('混凝土关键变量配对关系图', 
                      fontsize=16, fontweight='bold', y=1.01)
plt.tight_layout()
plt.savefig('pairplot_matrix.png', dpi=300, bbox_inches='tight')
plt.close()
print("已保存: pairplot_matrix.png")


components_all = ['Cement (component 1)(kg in a m^3 mixture)', 'Blast Furnace Slag (component 2)(kg in a m^3 mixture)', 'Fly Ash (component 3)(kg in a m^3 mixture)', 'Water  (component 4)(kg in a m^3 mixture)',
                  'Superplasticizer (component 5)(kg in a m^3 mixture)', 'Coarse Aggregate  (component 6)(kg in a m^3 mixture)', 'Fine Aggregate (component 7)(kg in a m^3 mixture)']
labels_all = ['水泥', '矿渣', '粉煤灰', '水', '减水剂', '粗骨料', '细骨料']

# 准备数据
data_melted = pd.melt(final_df[components_all])
data_melted['variable'] = data_melted['variable'].map(dict(zip(components_all, labels_all)))

plt.figure(figsize=(14, 7))
sns.violinplot(x='variable', y='value', data=data_melted, 
               palette='Set2', inner='box', cut=0)
plt.xlabel('成分类型', fontsize=12, fontweight='bold')
plt.ylabel('含量 (kg/m³)', fontsize=12, fontweight='bold')
plt.title('混凝土各成分含量分布小提琴图', fontsize=14, fontweight='bold')
plt.xticks(rotation=15)
plt.grid(True, alpha=0.3, axis='y', linestyle='--')
plt.tight_layout()
plt.savefig('violin_plot.png', dpi=300, bbox_inches='tight')
plt.close()
print("已保存: violin_plot.png")


# 选择三个代表性样本：强度最高、最低、中等
high_strength_idx = final_df['Concrete compressive strength(MPa, megapascals) '].idxmax()
low_strength_idx = final_df['Concrete compressive strength(MPa, megapascals) '].idxmin()
median_strength_idx = final_df.iloc[(final_df['Concrete compressive strength(MPa, megapascals) '] - final_df['Concrete compressive strength(MPa, megapascals) '].median()).abs().argsort()[0]].name

samples = [
    ('高强度配方', final_df.loc[high_strength_idx]),
    ('低强度配方', final_df.loc[low_strength_idx]),
    ('中等强度配方', final_df.loc[median_strength_idx])
]

categories = ['水泥', '矿渣', '粉煤灰', '水', '减水剂', '粗骨料', '细骨料']
categories_en = ['Cement (component 1)(kg in a m^3 mixture)', 'Blast Furnace Slag (component 2)(kg in a m^3 mixture)', 'Fly Ash (component 3)(kg in a m^3 mixture)', 'Water  (component 4)(kg in a m^3 mixture)',
                 'Superplasticizer (component 5)(kg in a m^3 mixture)', 'Coarse Aggregate  (component 6)(kg in a m^3 mixture)', 'Fine Aggregate (component 7)(kg in a m^3 mixture)']

# 归一化数据到0-100
max_values = final_df[categories_en].max()
normalized_data = []
for name, sample in samples:
    values = [sample[cat] / max_values[cat] * 100 for cat in categories_en]
    normalized_data.append((name, values))

# 雷达图需要闭合，所以要重复第一个值
angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
angles += angles[:1]

fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
for idx, (name, values) in enumerate(normalized_data):
    values += values[:1]  # 闭合
    ax.plot(angles, values, 'o-', linewidth=2, label=name, color=colors[idx])
    ax.fill(angles, values, alpha=0.15, color=colors[idx])

ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories, fontsize=11, fontweight='bold')
ax.set_ylim(0, 100)
ax.set_yticks([20, 40, 60, 80, 100])
ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'], fontsize=9)
ax.grid(True, linestyle='--', alpha=0.5)
ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=11)
plt.title('不同强度配方的成分对比雷达图', fontsize=14, 
          fontweight='bold', y=1.08)
plt.tight_layout()
plt.savefig('09_radar_chart.png', dpi=300, bbox_inches='tight')
plt.close()
print("已保存: radar_chart.png")