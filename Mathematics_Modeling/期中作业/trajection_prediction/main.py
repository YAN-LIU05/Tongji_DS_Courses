import os
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import RandomForestRegressor

from deal import final_deal, process_all_files
from src import parse_trajectory, generate_train_samples, predict_and_evaluate
 
def main():
    print('轨迹预测模型训练与评估')
    print('=' * 50)
    train_dir = 'train'
    train_masked_dir = 'train_masked'
    test_masked_dir = 'test_masked'
    train_predict_dir = 'train_predictions'
    test_predict_dir = 'test_predictions'
    test_file_dir = 'test_file'
    for directory in [train_dir, train_masked_dir, train_predict_dir, test_predict_dir, test_file_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)

    print('加载训练数据...')
    all_train_samples = []
    train_file_count = len(os.listdir(train_dir))
    for i, file_name in enumerate(os.listdir(train_dir)):
        print(f'处理train文件 ({i + 1}/{train_file_count}): {file_name}')
        file_path = os.path.join(train_dir, file_name)
        df = parse_trajectory(file_path)
        samples = generate_train_samples(df)
        all_train_samples.extend(samples)
        print(f'  从 {file_name} 生成了 {len(samples)} 个训练样本')

    print(f'\n总训练样本数: {len(all_train_samples)}')
    if len(all_train_samples) == 0:
        print('错误: 没有足够的训练样本，请检查数据目录')
        return

    print('\n准备训练模型...')
    train_df = pd.DataFrame(all_train_samples)
    feature_columns = ['prev_lon', 'prev_lat', 'next_lon', 'next_lat', 'rel_time', 'total_delta',
                       'prev_speed', 'prev_direction', 'prev_curvature', 'next_speed', 'next_direction', 'next_curvature']
    X = train_df[feature_columns]
    y = train_df[['target_lon', 'target_lat']]

    # 特征标准化
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled_df = pd.DataFrame(X_scaled, columns=feature_columns)

    X_train, X_val, y_train, y_val = train_test_split(X_scaled_df, y, test_size=0.2, random_state=42)

    print(f'训练集大小: {len(X_train)}')
    print(f'验证集大小: {len(X_val)}')

    print('\n训练随机森林回归模型...')
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_val_pred = model.predict(X_val)
    val_mse = mean_squared_error(y_val, y_val_pred)
    print(f'验证集MSE: {val_mse:.6f}')

    print('\n在训练数据上执行预测和评估:')
    avg_mse, avg_frechet = predict_and_evaluate(
        train_masked_dir, train_dir, model, 
        train_predict_dir, evaluate=True, is_test=False, scaler=scaler
    )
    
    if avg_mse is not None and avg_frechet is not None:
        print(f"\n总体评估结果:")
        print(f"平均MSE: {avg_mse:.6f}")
        print(f"平均Frechet距离: {avg_frechet:.6f}")
    print('\n训练数据预测已完成，结果已保存到 train_predictions 目录')

    if os.path.exists(test_masked_dir) and len(os.listdir(test_masked_dir)) > 0:
        print('\n发现测试数据，开始预测:')
        predict_and_evaluate(test_masked_dir, None, model, test_predict_dir, evaluate=False, is_test=True, scaler=scaler)
        print('\n测试数据预测已完成，结果已保存到 test_predictions 目录')
        print('特定格式的测试结果已保存到 test_file 目录')
    else:
        print('\n未找到测试数据目录或目录为空')
    
    final_deal()
    process_all_files()
    
    

if __name__ == "__main__":
    main()


