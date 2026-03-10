import pandas as pd
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

# 读取两个Parquet文件
df_A = pd.read_parquet('data/MicroLens_1M_x1/item_info.parquet')
df_B = pd.read_parquet('pca_all/pca_vectors.parquet')

# 查看两个DataFrame的结构
print(f"ParquetA形状: {df_A.shape}")
print(f"ParquetB形状: {df_B.shape}")

# 创建一个新的DataFrame来保存结果
# 保留第一行，然后用ParquetB的数据替换后面的行
new_df = df_A.copy()

# 首先检查item_emb_d128列的数据类型
print(f"item_emb_d128类型: {type(df_A.iloc[0]['item_emb_d128'])}")

# 直接替换从第二行开始的所有行的item_emb_d128列
for i in range(len(df_B)):
    if i + 1 < len(new_df):  # 确保不会超出范围
        # 获取B中的向量
        vector = df_B.loc[i, 'pca_vector']
        
        # 直接替换A中对应行的item_emb_d128值
        # 根据列的实际类型可能需要调整
        if isinstance(vector, np.ndarray):
            new_df.at[i + 1, 'item_emb_d128'] = vector.tolist()  # 如果是numpy数组，转为列表
        else:
            new_df.at[i + 1, 'item_emb_d128'] = vector

# 保存更新后的DataFrame
# 使用to_parquet直接保存，让pandas处理schema
new_df.to_parquet('data/MicroLens_1M_x1/item_info_new.parquet')

print("替换完成并保存为updated_parquetA.parquet")