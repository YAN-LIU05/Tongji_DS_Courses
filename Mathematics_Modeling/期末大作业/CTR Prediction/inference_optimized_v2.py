import torch
from transformers import Qwen2_5_VLForConditionalGeneration, AutoTokenizer, AutoProcessor
from qwen_vl_utils import process_vision_info
import os
import torch.nn.functional as F
from tqdm import tqdm
import numpy as np
import pandas as pd
import json
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MultimodalEmbeddingExtractor:
    """
    多模态嵌入向量提取器
    使用Qwen2.5-VL-7B模型提取多模态特征
    
    支持两种降维方案：
    1. 神经网络降维：直接输出128维向量
    2. 原始输出：输出1024维向量，后续使用PCA降维
    """
    
    def __init__(self, model_path="qwen2.5-vl-7B", device="auto", use_neural_reduction=True):
        """
        初始化多模态嵌入向量提取器
        
        参数:
        model_path: 模型路径
        device: 设备选择，默认自动选择
        use_neural_reduction: 是否使用神经网络降维，True为方案A，False为方案B
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() and device != "cpu" else "cpu")
        self.use_neural_reduction = use_neural_reduction
        logger.info(f"使用设备: {self.device}")
        logger.info(f"降维方案: {'神经网络降维' if use_neural_reduction else 'PCA降维'}")
        
        # 加载Qwen2.5-VL模型
        logger.info("加载Qwen2.5-VL模型...")
        self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            model_path, torch_dtype="auto", device_map="auto"
        )
        
        # 加载处理器
        logger.info("加载模型处理器...")
        self.processor = AutoProcessor.from_pretrained(model_path)
        
        # 设置模型为评估模式
        self.model.eval()
        
        # 目标维度（Task 1要求）
        self.target_dim = 128
        
        if use_neural_reduction:
            # 方案A: 使用神经网络降维层，直接输出128维
            logger.info("使用神经网络降维层，直接输出128维向量")
            # 首先获取模型的隐藏状态维度
            self.hidden_dim = 3584  # Qwen2.5-VL-7B的隐藏状态维度
            self.dimension_reducer = torch.nn.Sequential(
                torch.nn.Linear(self.hidden_dim, 1024),  # 3584 -> 1024
                torch.nn.ReLU(),
                torch.nn.Dropout(0.1),
                torch.nn.Linear(1024, 512),   # 1024 -> 512
                torch.nn.ReLU(),
                torch.nn.Dropout(0.1),
                torch.nn.Linear(512, 256),    # 512 -> 256
                torch.nn.ReLU(),
                torch.nn.Dropout(0.1),
                torch.nn.Linear(256, self.target_dim),  # 256 -> 128
                torch.nn.Tanh()  # 使用Tanh激活函数限制输出范围
            ).to(self.device)
        else:
            # 方案B: 不使用降维层，输出原始1024维，后续使用PCA
            logger.info("输出原始1024维向量，后续使用PCA降维")
            self.dimension_reducer = None
        
        logger.info(f"模型加载完成，目标维度: {self.target_dim if use_neural_reduction else 1024}")
    
    def get_embeddings(self, messages, pooling_method="mean"):
        """
        获取多模态输入的嵌入向量
        
        参数:
        messages: 包含文本和图像的消息列表
        pooling_method: 池化方法，可选 'mean'(平均池化)、'last'(最后一个token)或'cls'(第一个token)
        
        返回:
        嵌入向量（128维或1024维，取决于降维方案）
        """
        try:
            # 准备输入
            text = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
            vision_result = process_vision_info(messages)
            
            # 处理返回的视觉信息
            if isinstance(vision_result, tuple) and len(vision_result) >= 2:
                image_inputs, video_inputs = vision_result[0], vision_result[1]
            else:
                image_inputs, video_inputs = [], []
            
            # 处理本地图像路径
            if image_inputs:
                for i, img in enumerate(image_inputs):
                    if isinstance(img, str) and os.path.exists(img):
                        from PIL import Image
                        image_inputs[i] = Image.open(img).convert('RGB')
            
            # 使用处理器准备输入
            inputs = self.processor(
                text=[text],
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt",
            )
            inputs = inputs.to(self.device)
            
            # 使用模型获取嵌入向量(不生成文本)
            with torch.no_grad():
                outputs = self.model(**inputs, output_hidden_states=True)
                # 获取倒数第二层的隐藏状态
                last_hidden_states = outputs.hidden_states[-2]
                
                if pooling_method == "last":
                    # 使用最后一个token的隐藏状态作为整个序列的表示
                    embedding = last_hidden_states[0, -1, :]
                elif pooling_method == "cls":
                    # 使用第一个token(CLS token)的隐藏状态
                    embedding = last_hidden_states[0, 0, :]
                else:  # 默认使用mean
                    # 使用所有token的平均隐藏状态
                    embedding = torch.mean(last_hidden_states, dim=1).squeeze()
                
                # 确保数据类型为float32
                embedding = embedding.to(torch.float32)
                
                if self.use_neural_reduction:
                    # 方案A: 通过神经网络降维层得到128维向量
                    embedding = self.dimension_reducer(embedding.unsqueeze(0)).squeeze()
                    # 进行L2归一化
                    embedding = F.normalize(embedding.unsqueeze(0), p=2, dim=1).squeeze(0).cpu().numpy()
                else:
                    # 方案B: 直接输出1024维向量，只进行L2归一化
                    embedding = F.normalize(embedding.unsqueeze(0), p=2, dim=1).squeeze(0).cpu().numpy()
            
            return embedding
            
        except Exception as e:
            logger.error(f"获取嵌入向量时出错: {e}")
            # 返回零向量作为占位符
            return np.zeros(self.target_dim if self.use_neural_reduction else self.hidden_dim)
    
    def extract_item_embedding(self, item_data, images_folder):
        """
        为单个item提取嵌入向量
        
        参数:
        item_data: 包含item信息的字典
        images_folder: 图像文件夹路径
        
        返回:
        嵌入向量（128维或1024维）
        """
        item_id = item_data.get('item_id', '')
        title = item_data.get('title', '')
        attributes = item_data.get('attributes', {})
        
        # 构建图像路径
        image_path = os.path.join(images_folder, f"{item_id}.jpg")
        
        # 构建属性文本
        if isinstance(attributes, dict):
            attr_text = " ".join([f"{k}: {v}" for k, v in attributes.items()])
        else:
            attr_text = str(attributes) if attributes else ""
        
        # 构建完整的文本描述
        full_text = f"Title: {title}"
        if attr_text:
            full_text += f" | Attributes: {attr_text}"
        
        # 构建消息
        messages = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "You are a helpful assistant that analyzes video content and provides comprehensive descriptions."
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "image": image_path,
                    },
                    {
                        "type": "text",
                        "text": f"Please analyze this video content: {full_text}"
                    }
                ],
            }
        ]
        
        # 获取嵌入向量
        embedding = self.get_embeddings(messages)
        
        return embedding

def process_items_and_generate_embeddings(parquet_file, images_folder, output_file, batch_size=100, use_neural_reduction=True):
    """
    处理parquet文件，为每个item生成embedding并保存结果
    
    参数:
    parquet_file: 输入的parquet文件路径
    images_folder: 存储图片的文件夹路径
    output_file: 输出的parquet文件路径
    batch_size: 处理的批次大小，用于中间保存
    use_neural_reduction: 是否使用神经网络降维
    """
    
    # 读取parquet文件
    logger.info(f"正在读取parquet文件: {parquet_file}")
    df = pd.read_parquet(parquet_file)
    
    # 检查列名并确保数据格式正确
    cols = df.columns.tolist()
    id_col = cols[0]  # 假设第一列是item_id
    text_col = cols[1] if len(cols) > 1 else 'title'  # 假设第二列是文本内容
    
    # 创建新列用于存储embeddings
    df['embedding'] = None
    
    # 检查是否存在中间结果文件，如果存在则加载
    temp_file = f"{output_file}.temp.parquet"
    if os.path.exists(temp_file):
        logger.info(f"发现中间结果文件，加载已处理的数据...")
        temp_df = pd.read_parquet(temp_file)
        
        # 获取已处理的item_ids
        processed_ids = set(temp_df[id_col].tolist())
        logger.info(f"已处理的item数量: {len(processed_ids)}")
        
        # 更新主DataFrame中已处理的embeddings
        df = pd.concat([df[~df[id_col].isin(processed_ids)], temp_df])
    else:
        processed_ids = set()
    
    # 获取待处理的items
    items_to_process = df[~df[id_col].isin(processed_ids)].copy()
    
    if len(items_to_process) == 0:
        logger.info("所有数据已处理完毕，无需再次处理")
        df.to_parquet(output_file)
        return
    
    logger.info(f"待处理的item数量: {len(items_to_process)}")
    
    # 创建嵌入向量提取器
    extractor = MultimodalEmbeddingExtractor(use_neural_reduction=use_neural_reduction)
    
    # 初始化进度条
    pbar = tqdm(total=len(items_to_process), desc="处理items")
    
    # 批次处理
    batch_count = 0
    for idx, row in items_to_process.iterrows():
        item_id = row[id_col]
        text_content = row[text_col]
        
        # 构建item数据
        item_data = {
            'item_id': item_id,
            'title': text_content,
            'attributes': row.get('attributes', {}) if 'attributes' in row else {}
        }
        
        try:
            # 提取嵌入向量
            embedding = extractor.extract_item_embedding(item_data, images_folder)
            
            # 保存结果
            df.at[idx, 'embedding'] = embedding.tolist()
            processed_ids.add(item_id)
            
            pbar.update(1)
            batch_count += 1
            
            # 每处理batch_size个item保存一次中间结果
            if batch_count % batch_size == 0:
                # 保存中间结果
                temp_save_df = df[df[id_col].isin(processed_ids)].copy()
                temp_save_df.to_parquet(temp_file)
                logger.info(f"已保存中间结果，当前处理了 {len(processed_ids)} 个items")
                
        except Exception as e:
            logger.error(f"处理item {item_id}时出错: {str(e)}")
            # 使用零向量作为占位符
            target_dim = 128 if use_neural_reduction else 3584
            df.at[idx, 'embedding'] = np.zeros(target_dim).tolist()
            continue
    
    # 关闭进度条
    pbar.close()
    
    # 保存最终结果
    logger.info("处理完毕，保存最终结果...")
    df.to_parquet(output_file)
    
    # 删除临时文件
    if os.path.exists(temp_file):
        os.remove(temp_file)
    
    logger.info(f"结果已保存至: {output_file}")
    
    # 验证结果
    test_df = pd.read_parquet(output_file)
    sample_embedding = np.array(test_df.iloc[0]['embedding'])
    logger.info(f"最终embedding维度: {sample_embedding.shape}")

def main():
    """
    主函数
    """
    # 参数设置
    parquet_file = "data/MicroLens_1M_x1/item_feature.parquet"  # 输入文件路径
    images_folder = "data/item_images"  # 图像文件夹路径
    
    # 选择降维方案
    use_neural_reduction = True  # True: 神经网络降维, False: PCA降维
    
    if use_neural_reduction:
        output_file = "data/qwen_7B_vl_128d_embeddings.parquet"  # 方案A: 直接输出128维
        logger.info("使用方案A: 神经网络降维，直接输出128维向量")
    else:
        output_file = "data/qwen_7B_vl_3584d_embeddings.parquet"  # 方案B: 输出3584维，后续PCA
        logger.info("使用方案B: 输出3584维向量，后续使用PCA降维")
    
    logger.info("=" * 60)
    logger.info("Task 1: 多模态Item嵌入向量生成")
    logger.info("=" * 60)
    logger.info(f"输入文件: {parquet_file}")
    logger.info(f"图像文件夹: {images_folder}")
    logger.info(f"输出文件: {output_file}")
    logger.info(f"降维方案: {'神经网络降维' if use_neural_reduction else 'PCA降维'}")
    logger.info("=" * 60)
    
    # 检查输入文件
    if not os.path.exists(parquet_file):
        logger.error(f"输入文件不存在: {parquet_file}")
        return
    
    if not os.path.exists(images_folder):
        logger.warning(f"图像文件夹不存在: {images_folder}")
    
    # 处理数据
    process_items_and_generate_embeddings(
        parquet_file=parquet_file,
        images_folder=images_folder,
        output_file=output_file,
        batch_size=1000,
        use_neural_reduction=use_neural_reduction
    )
    
    # 保存模型信息
    model_info = {
        "task": "Task 1: Multimodal Item Embedding",
        "model_type": "Qwen2.5-VL-7B",
        "reduction_method": "neural_network" if use_neural_reduction else "pca",
        "output_dimension": 128 if use_neural_reduction else 3584,
        "fusion_method": "multimodal_fusion",
        "normalization": "L2",
        "pooling_method": "mean"
    }
    
    with open("model_info.json", "w") as f:
        json.dump(model_info, f, indent=4)
    
    logger.info("模型信息已保存到 model_info.json")
    logger.info("Task 1 嵌入向量生成完成!")

if __name__ == "__main__":
    main() 