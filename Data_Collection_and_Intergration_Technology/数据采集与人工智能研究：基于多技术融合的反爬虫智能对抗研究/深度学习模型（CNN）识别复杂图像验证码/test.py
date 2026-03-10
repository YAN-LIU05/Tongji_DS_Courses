"""
测试脚本 - 支持大小写不敏感匹配
"""
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm
import matplotlib.pyplot as plt
import os
import numpy as np
from sklearn.metrics import confusion_matrix
import seaborn as sns

import config
from utils.dataset import CaptchaDataset
from models.model import LightweightCaptchaCNN

def test_model(checkpoint_path, save_predictions=False, case_sensitive=False):
    """
    测试模型
    
    Args:
        checkpoint_path: 模型检查点路径
        save_predictions: 是否保存预测结果
        case_sensitive: 是否区分大小写（默认False，即不区分大小写）
    """
    print("="*60)
    print("开始测试模型")
    print(f"大小写敏感: {'是' if case_sensitive else '否'}")
    print("="*60)
    
    # 加载测试数据
    print("加载测试数据集...")
    test_dataset = CaptchaDataset(config.TEST_DIR, config.CHARSET, augment=False)
    test_loader = DataLoader(
        test_dataset, 
        batch_size=config.BATCH_SIZE, 
        shuffle=False, 
        num_workers=config.NUM_WORKERS,
        pin_memory=True
    )
    
    # 创建模型
    print("加载模型...")
    model = LightweightCaptchaCNN(num_classes=len(config.CHARSET), num_chars=config.NUM_CHARS)
    
    # 加载权重
    checkpoint = torch.load(checkpoint_path, map_location=config.DEVICE)
    model.load_state_dict(checkpoint['model_state_dict'])
    model = model.to(config.DEVICE)
    model.eval()
    
    print(f"模型加载完成 (训练时准确率: {checkpoint.get('accuracy', 'N/A'):.2f}%)")
    print(f"Epoch: {checkpoint.get('epoch', 'N/A')}")
    
    # 评估
    idx_to_char = {idx: char for idx, char in enumerate(config.CHARSET)}
    
    all_predictions = []
    all_labels = []
    all_predictions_original = []  # 保存原始预测（未转换大小写）
    all_labels_original = []  # 保存原始标签（未转换大小写）
    wrong_samples = []
    char_level_stats = {i: {'correct': 0, 'total': 0} for i in range(config.NUM_CHARS)}
    
    print("\n开始测试...")
    with torch.no_grad():
        for images, labels in tqdm(test_loader, desc="测试进度"):
            images = images.to(config.DEVICE)
            labels_np = labels.numpy()
            
            outputs = model(images)
            predictions = [torch.argmax(output, dim=1) for output in outputs]
            predictions = torch.stack(predictions, dim=1).cpu().numpy()
            
            # 收集结果
            for i in range(len(images)):
                pred_str_original = ''.join([idx_to_char[idx] for idx in predictions[i]])
                true_str_original = ''.join([idx_to_char[idx] for idx in labels_np[i]])
                
                # 保存原始版本
                all_predictions_original.append(pred_str_original)
                all_labels_original.append(true_str_original)
                
                # 根据case_sensitive参数决定是否转换大小写
                if case_sensitive:
                    pred_str = pred_str_original
                    true_str = true_str_original
                else:
                    pred_str = pred_str_original.lower()
                    true_str = true_str_original.lower()
                
                all_predictions.append(pred_str)
                all_labels.append(true_str)
                
                # 统计每个位置的准确率
                for pos in range(config.NUM_CHARS):
                    char_level_stats[pos]['total'] += 1
                    if case_sensitive:
                        if predictions[i][pos] == labels_np[i][pos]:
                            char_level_stats[pos]['correct'] += 1
                    else:
                        # 不区分大小写的比较
                        pred_char = idx_to_char[predictions[i][pos]].lower()
                        true_char = idx_to_char[labels_np[i][pos]].lower()
                        if pred_char == true_char:
                            char_level_stats[pos]['correct'] += 1
                
                if pred_str != true_str:
                    wrong_samples.append((images[i].cpu().numpy(), 
                                        true_str_original, 
                                        pred_str_original))
    
    # 计算指标
    total = len(all_predictions)
    correct = sum([1 for p, l in zip(all_predictions, all_labels) if p == l])
    accuracy = 100 * correct / total
    
    # 计算字符级准确率
    char_correct = sum([sum([1 for p, l in zip(pred, label) if p == l]) 
                        for pred, label in zip(all_predictions, all_labels)])
    char_total = total * config.NUM_CHARS
    char_accuracy = 100 * char_correct / char_total
    
    # 如果不区分大小写，也计算区分大小写时的准确率作为对比
    if not case_sensitive:
        strict_correct = sum([1 for p, l in zip(all_predictions_original, all_labels_original) if p == l])
        strict_accuracy = 100 * strict_correct / total
    
    print(f"\n{'='*60}")
    print("测试结果")
    print(f"{'='*60}")
    print(f"总样本数: {total}")
    print(f"正确预测: {correct}")
    print(f"错误预测: {total - correct}")
    
    if case_sensitive:
        print(f"整体准确率 (区分大小写): {accuracy:.2f}%")
    else:
        print(f"整体准确率 (不区分大小写): {accuracy:.2f}%")
        print(f"整体准确率 (严格区分大小写): {strict_accuracy:.2f}%")
    
    print(f"字符级准确率: {char_accuracy:.2f}%")
    
    # 计算每个位置的准确率
    print(f"\n各位置准确率 ({'区分大小写' if case_sensitive else '不区分大小写'}):")
    for pos in range(config.NUM_CHARS):
        pos_acc = 100 * char_level_stats[pos]['correct'] / char_level_stats[pos]['total']
        print(f"  位置 {pos+1}: {pos_acc:.2f}%")
    
    # 分析常见错误
    analyze_common_errors(all_predictions, all_labels, 
                         all_predictions_original, all_labels_original, 
                         case_sensitive)
    
    # 可视化
    visualize_errors(wrong_samples[:20], case_sensitive)
    if case_sensitive:
        plot_confusion_matrix(all_predictions_original, all_labels_original)
    
    # 保存预测结果
    if save_predictions:
        save_predictions_to_file(all_predictions_original, all_labels_original, 
                                all_predictions, all_labels, case_sensitive)
    
    return accuracy

def analyze_common_errors(predictions, labels, predictions_original, labels_original, case_sensitive):
    """分析常见的识别错误"""
    error_dict = {}
    
    # 使用原始版本来统计错误
    for pred_orig, label_orig, pred, label in zip(predictions_original, labels_original, 
                                                   predictions, labels):
        for i, (p_orig, l_orig, p, l) in enumerate(zip(pred_orig, label_orig, pred, label)):
            if p != l:  # 使用转换后的版本判断是否错误
                # 但显示原始字符
                key = f"{l_orig}->{p_orig}"
                if key not in error_dict:
                    error_dict[key] = 0
                error_dict[key] += 1
    
    if error_dict:
        print(f"\n{'='*60}")
        print(f"最常见的识别错误 (Top 10) - {'区分大小写' if case_sensitive else '不区分大小写'}:")
        print(f"{'='*60}")
        sorted_errors = sorted(error_dict.items(), key=lambda x: x[1], reverse=True)[:10]
        for error, count in sorted_errors:
            print(f"  {error}: {count} 次")
    else:
        print("\n🎉 没有识别错误！")

def plot_confusion_matrix(predictions, labels):
    """绘制混淆矩阵（针对每个位置）"""
    try:
        for pos in range(min(config.NUM_CHARS, 2)):
            y_true = [label[pos] for label in labels]
            y_pred = [pred[pos] for pred in predictions]
            
            unique_chars = sorted(set(y_true + y_pred))
            
            cm = confusion_matrix(y_true, y_pred, labels=unique_chars)
            
            plt.figure(figsize=(12, 10))
            sns.heatmap(cm, annot=False, fmt='d', cmap='Blues', 
                       xticklabels=unique_chars, yticklabels=unique_chars)
            plt.title(f'位置 {pos+1} 的混淆矩阵')
            plt.ylabel('真实标签')
            plt.xlabel('预测标签')
            plt.tight_layout()
            
            save_path = os.path.join(config.RESULTS_DIR, f'confusion_matrix_pos{pos+1}.png')
            plt.savefig(save_path, dpi=150)
            plt.close()
            
        print(f"\n混淆矩阵已保存到 {config.RESULTS_DIR}")
    except Exception as e:
        print(f"\n绘制混淆矩阵时出错: {e}")

def visualize_errors(wrong_samples, case_sensitive, num_display=20):
    """可视化错误案例"""
    if len(wrong_samples) == 0:
        mode = "区分大小写" if case_sensitive else "不区分大小写"
        print(f"\n🎉 没有错误案例！模型在{mode}模式下达到100%准确率！")
        return
    
    num_display = min(num_display, len(wrong_samples))
    
    fig, axes = plt.subplots(4, 5, figsize=(15, 12))
    axes = axes.ravel()
    
    for idx in range(num_display):
        img, true_label, pred_label = wrong_samples[idx]
        
        if img.shape[0] == 1:
            img_display = img.squeeze()
        else:
            img_display = np.transpose(img, (1, 2, 0))
        
        axes[idx].imshow(img_display, cmap='gray')
        
        title = f'True: {true_label}\nPred: {pred_label}'
        color = 'red'
        axes[idx].set_title(title, fontsize=10, color=color)
        axes[idx].axis('off')
    
    for idx in range(num_display, 20):
        axes[idx].axis('off')
    
    plt.tight_layout()
    mode_suffix = "case_sensitive" if case_sensitive else "case_insensitive"
    save_path = os.path.join(config.RESULTS_DIR, f'error_cases_{mode_suffix}.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"\n错误案例可视化已保存到 {save_path}")

def save_predictions_to_file(predictions_original, labels_original, 
                            predictions_normalized, labels_normalized, case_sensitive):
    """保存预测结果到文件"""
    mode = "case_sensitive" if case_sensitive else "case_insensitive"
    save_path = os.path.join(config.RESULTS_DIR, f'predictions_{mode}.txt')
    
    with open(save_path, 'w', encoding='utf-8') as f:
        if case_sensitive:
            f.write("真实标签\t预测标签\t是否正确\n")
            for pred, label in zip(predictions_original, labels_original):
                is_correct = "✓" if pred == label else "✗"
                f.write(f"{label}\t{pred}\t{is_correct}\n")
        else:
            f.write("真实标签(原始)\t预测标签(原始)\t真实标签(小写)\t预测标签(小写)\t是否正确\n")
            for pred_orig, label_orig, pred_norm, label_norm in zip(
                predictions_original, labels_original, 
                predictions_normalized, labels_normalized):
                is_correct = "✓" if pred_norm == label_norm else "✗"
                f.write(f"{label_orig}\t{pred_orig}\t{label_norm}\t{pred_norm}\t{is_correct}\n")
    
    print(f"预测结果已保存到 {save_path}")

if __name__ == '__main__':
    # 查找最新的checkpoint
    if not os.path.exists(config.CHECKPOINT_DIR):
        print(f"错误: checkpoint目录不存在: {config.CHECKPOINT_DIR}")
        exit(1)
    
    checkpoints = [f for f in os.listdir(config.CHECKPOINT_DIR) if f.endswith('.pth')]
    
    if not checkpoints:
        print("错误: 没有找到训练好的模型")
        print("请先运行 train.py 训练模型")
        exit(1)
    
    latest_checkpoint = max(
        checkpoints, 
        key=lambda x: os.path.getctime(os.path.join(config.CHECKPOINT_DIR, x))
    )
    checkpoint_path = os.path.join(config.CHECKPOINT_DIR, latest_checkpoint)
    print(f"使用checkpoint: {checkpoint_path}\n")
    
    # 运行测试 - 不区分大小写
    print("\n" + "="*60)
    print("模式: 不区分大小写")
    print("="*60)
    accuracy_insensitive = test_model(checkpoint_path, save_predictions=True, case_sensitive=False)
    
    print(f"\n{'='*60}")
    print(f"测试完成！准确率(不区分大小写): {accuracy_insensitive:.2f}%")
    print(f"{'='*60}")
    
    # 可选：也运行区分大小写的测试进行对比
    # print("\n\n" + "="*60)
    # print("模式: 区分大小写")
    # print("="*60)
    # accuracy_sensitive = test_model(checkpoint_path, save_predictions=True, case_sensitive=True)
    # print(f"\n{'='*60}")
    # print(f"测试完成！准确率(区分大小写): {accuracy_sensitive:.2f}%")
    # print(f"{'='*60}")