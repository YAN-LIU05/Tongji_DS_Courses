"""
改进的数据集处理 - 更强的数据增强
"""
import torch
from torch.utils.data import Dataset
import cv2
import os
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import random

class CaptchaDataset(Dataset):
    def __init__(self, data_dir, charset, augment=False):
        self.data_dir = data_dir
        self.charset = charset
        self.char_to_idx = {char: idx for idx, char in enumerate(charset)}
        self.augment = augment
        
        self.image_files = [f for f in os.listdir(data_dir) 
                           if f.endswith(('.jpg', '.png', '.jpeg'))]
        print(f"加载数据集 {data_dir}: 共 {len(self.image_files)} 张图片")
        
    def __len__(self):
        return len(self.image_files)
    
    def __getitem__(self, idx):
        img_name = self.image_files[idx]
        img_path = os.path.join(self.data_dir, img_name)
        
        # 读取图像
        image = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            print(f"警告: 无法读取图片 {img_path}")
            image = np.zeros((60, 160), dtype=np.uint8)
        
        # 确保尺寸正确
        if image.shape != (60, 160):
            image = cv2.resize(image, (160, 60))
        
        # 数据增强
        if self.augment:
            image = self.strong_augmentation(image)
        
        # 归一化到[-1, 1]区间（更好的性能）
        image = image.astype(np.float32) / 255.0
        image = (image - 0.5) / 0.5
        
        # 转换为CHW格式
        image = np.expand_dims(image, axis=0)
        
        # 提取标签
        label = os.path.splitext(img_name)[0]
        
        # 处理标签
        while '.' in label:
            label = os.path.splitext(label)[0]
        
        if len(label) != 5:
            print(f"警告: 标签长度不为5: {label}")
            label = label[:5].ljust(5, '0')
        
        # 编码标签
        encoded_label = []
        for char in label:
            if char in self.char_to_idx:
                encoded_label.append(self.char_to_idx[char])
            else:
                print(f"⚠️ 字符 '{char}' 不在字符集中")
                encoded_label.append(0)
        
        return torch.FloatTensor(image), torch.LongTensor(encoded_label)
    
    def strong_augmentation(self, image):
        """更强的数据增强"""
        # 转为PIL Image方便处理
        pil_img = Image.fromarray(image)
        
        # 1. 随机亮度调整 (70%概率)
        if random.random() < 0.7:
            enhancer = ImageEnhance.Brightness(pil_img)
            pil_img = enhancer.enhance(random.uniform(0.7, 1.3))
        
        # 2. 随机对比度调整 (70%概率)
        if random.random() < 0.7:
            enhancer = ImageEnhance.Contrast(pil_img)
            pil_img = enhancer.enhance(random.uniform(0.7, 1.3))
        
        # 3. 随机锐化 (30%概率)
        if random.random() < 0.3:
            enhancer = ImageEnhance.Sharpness(pil_img)
            pil_img = enhancer.enhance(random.uniform(0.5, 2.0))
        
        # 转回numpy
        image = np.array(pil_img)
        
        # 4. 随机噪声 (50%概率)
        if random.random() < 0.5:
            noise_type = random.choice(['gaussian', 'salt_pepper', 'speckle'])
            
            if noise_type == 'gaussian':
                noise = np.random.normal(0, random.uniform(5, 15), image.shape)
                image = np.clip(image + noise, 0, 255).astype(np.uint8)
            
            elif noise_type == 'salt_pepper':
                prob = random.uniform(0.01, 0.03)
                mask = np.random.random(image.shape)
                image[mask < prob/2] = 0
                image[mask > 1 - prob/2] = 255
            
            elif noise_type == 'speckle':
                noise = np.random.randn(*image.shape) * random.uniform(10, 20)
                image = np.clip(image + image * noise / 255, 0, 255).astype(np.uint8)
        
        # 5. 随机模糊 (30%概率)
        if random.random() < 0.3:
            blur_type = random.choice(['gaussian', 'median'])
            if blur_type == 'gaussian':
                ksize = random.choice([3, 5])
                image = cv2.GaussianBlur(image, (ksize, ksize), 0)
            else:
                ksize = random.choice([3, 5])
                image = cv2.medianBlur(image, ksize)
        
        # 6. 随机轻微旋转 (40%概率)
        if random.random() < 0.4:
            angle = random.uniform(-3, 3)
            h, w = image.shape
            M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1.0)
            image = cv2.warpAffine(image, M, (w, h), 
                                  borderMode=cv2.BORDER_REPLICATE)
        
        # 7. 随机轻微缩放 (40%概率)
        if random.random() < 0.4:
            scale = random.uniform(0.95, 1.05)
            h, w = image.shape
            new_h, new_w = int(h * scale), int(w * scale)
            image = cv2.resize(image, (new_w, new_h))
            
            # 裁剪或填充回原尺寸
            if new_h > h or new_w > w:
                start_h = (new_h - h) // 2
                start_w = (new_w - w) // 2
                image = image[start_h:start_h+h, start_w:start_w+w]
            else:
                pad_h = (h - new_h) // 2
                pad_w = (w - new_w) // 2
                image = cv2.copyMakeBorder(image, pad_h, h-new_h-pad_h, 
                                          pad_w, w-new_w-pad_w,
                                          cv2.BORDER_REPLICATE)
        
        return image