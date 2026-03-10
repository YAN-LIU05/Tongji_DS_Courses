import os
import random
import numpy as np
import torch
from PIL import Image
from torchvision import transforms
from datasets import load_dataset
from accelerate.logging import get_logger

# 数据集映射字典，用于指定不同数据集的图像ID列和诗词列的名称
DATASET_MAPPING = {
    "Paint4Poem-Web-famous-subset": ("image_id", "诗词"),
}

def convert_png_to_jpeg(root_dir):
    """将PNG格式图片转换为JPEG格式
    
    Args:
        root_dir: 包含PNG图片的根目录
    """
    for folder, _, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith('.png'):
                png_path = os.path.join(folder, file)
                jpeg_path = os.path.splitext(png_path)[0] + '.jpeg'
                try:
                    with Image.open(png_path) as img:
                        rgb_img = img.convert('RGB')
                        rgb_img.save(jpeg_path, 'JPEG')
                    print(f"已转换: {png_path} -> {jpeg_path}")
                except Exception as e:
                    print(f"转换失败: {png_path}, 错误: {e}")

def parse_dataset_args(parser):
    """配置数据集相关的命令行参数解析器
    
    Args:
        parser: ArgumentParser对象
    """
    # 各种命令行参数的定义和说明
    parser.add_argument(
        "--dataset",
        type=str,
        default=None,
        help="数据集名称(来自HuggingFace hub)。设为None表示使用本地数据集"
    )
    parser.add_argument(
        "--dataset_config",
        type=str,
        default=None,
        help="数据集配置名称，如果只有一个配置则保持为None"
    )
    parser.add_argument(
        "--data_direction",
        type=str,
        default="./Paint4Poem-Web-famous-subset",
        help="包含训练数据的文件夹（需包含POEM_IMAGE.csv和images/目录）"
    )
    parser.add_argument(
        "--image_column", 
        type=str, 
        default="image_id", 
        help="数据集中包含图像ID的列名"
    )
    parser.add_argument(
        "--caption_column",
        type=str,
        default="poem",
        help="数据集中包含诗词或诗词列表的列名"
    )
    parser.add_argument(
        "--max_samples",
        type=int,
        default=None,
        help="用于调试或快速训练时，限制训练样本数量"
    )

# 创建日志记录器
logger = get_logger(__name__, log_level="INFO")

def prepare_dataset(args, accelerator, tokenizer):
    """准备训练数据集
    
    Args:
        args: 包含数据集配置的命令行参数
        accelerator: 用于分布式训练的加速器对象
        tokenizer: 用于处理文本的分词器
        
    Returns:
        tuple: (训练数据集, 数据加载器)
    """
    # 根据参数加载数据集
    if args.dataset is not None:
        # 从HuggingFace hub加载数据集
        dataset = load_dataset(
            args.dataset,
            args.dataset_config,
            cache_dir=args.cache_direction,
            data_dir=args.data_direction,
        )
    else:
        # 从本地CSV文件加载数据集
        dataset = load_dataset(
            "csv",
            data_files={"train": os.path.join(args.data_direction, "POEM_IMAGE.csv")},
            cache_dir=args.cache_direction,
            delimiter="\t" if os.path.exists(os.path.join(args.data_direction, "POEM_IMAGE.csv")) else ",",
        )

    # 获取并验证数据集的列名
    column_names = dataset["train"].column_names
    dataset_columns = DATASET_MAPPING.get(args.data_direction, None)
    # 确定图像列和标题列的名称
    image_column = dataset_columns[0] if dataset_columns is not None else column_names[0] if args.image_column is None else args.image_column
    caption_column = dataset_columns[1] if dataset_columns is not None else column_names[1] if args.caption_column is None else args.caption_column
    
    # 验证列名是否存在
    if image_column not in column_names:
        raise ValueError(f"--image_column 值 '{image_column}' 必须是以下之一：{', '.join(column_names)}")
    if caption_column not in column_names:
        raise ValueError(f"--caption_column 值 '{caption_column}' 必须是以下之一：{', '.join(column_names)}")

    def tokenize_captions(examples, is_train=True):
        """将文本转换为token ID
        
        Args:
            examples: 包含文本的样本
            is_train: 是否为训练模式（影响多个标题时的选择策略）
        """
        captions = []
        for caption in examples[caption_column]:
            if isinstance(caption, str):
                captions.append(caption)
            elif isinstance(caption, (list, np.ndarray)):
                # 训练时随机选择一个标题，测试时使用第一个
                captions.append(random.choice(caption) if is_train else caption[0])
            else:
                raise ValueError(f"标题列 `{caption_column}` 应包含字符串或字符串列表。")
        # 使用tokenizer处理文本
        inputs = tokenizer(
            captions, max_length=tokenizer.model_max_length, padding="max_length", truncation=True, return_tensors="pt"
        )
        return inputs.input_ids

    # 定义图像预处理转换
    train_transforms = transforms.Compose(
        [
            transforms.Resize(args.image_size, interpolation=transforms.InterpolationMode.BILINEAR),
            transforms.CenterCrop(args.image_size) if args.center_crop else transforms.RandomCrop(args.image_size),
            transforms.RandomHorizontalFlip() if args.random_flip else transforms.Lambda(lambda x: x),
            transforms.ToTensor(),
            transforms.Normalize([0.5], [0.5]),
        ]
    )

    def preprocess_train(examples):
        """预处理训练样本
        
        Args:
            examples: 包含图像ID的样本
        """
        images = []
        for image_id in examples[image_column]:
            image_path = os.path.join(args.data_direction, "images", f"{image_id}.jpeg")
            try:
                # 加载并转换图像
                image = Image.open(image_path)
                images.append(image.convert("RGB"))
            except Exception as e:
                # 图像加载失败时使用白色图像代替
                logger.error(f"无法加载图像 {image_path}: {str(e)}")
                white_image = Image.new("RGB", (args.image_size, args.image_size), (255, 255, 255))
                images.append(white_image)
                logger.info(f"使用白色图像更换，避免影响模型训练")
        
        # 应用图像转换并生成token
        examples["pixel_values"] = [train_transforms(image) for image in images]
        examples["input_ids"] = tokenize_captions(examples)
        return examples

    # 使用accelerator确保在分布式环境中正确处理数据集
    with accelerator.main_process_first():
        if args.max_samples is not None:
            # 如果指定了最大样本数，随机选择样本
            dataset["train"] = dataset["train"].shuffle(random_seed=args.random_seed).select(range(args.max_samples))
        train_dataset = dataset["train"].with_transform(preprocess_train)

    def collate_fn(examples):
        """数据批次整理函数
        
        Args:
            examples: 批次中的样本列表
        Returns:
            dict: 包含处理后的像素值和token ID
        """
        pixel_values = torch.stack([example["pixel_values"] for example in examples])
        pixel_values = pixel_values.to(memory_format=torch.contiguous_format).float()
        input_ids = torch.stack([example["input_ids"] for example in examples])
        return {"pixel_values": pixel_values, "input_ids": input_ids}

    # 创建数据加载器
    train_dataloader = torch.utils.data.DataLoader(
        train_dataset,
        shuffle=True,
        collate_fn=collate_fn,
        batch_size=args.batch_size,
        num_workers=args.num_workers,
    )
    
    return train_dataset, train_dataloader