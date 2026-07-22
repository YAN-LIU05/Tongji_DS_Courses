import os
import cv2
import numpy as np
import random

input_folder = 'data/test'
output_folder = 'data_new/test'

def add_gaussian_noise(image, mean=0, std=50):
    noise = np.random.normal(mean, std, image.shape).astype(np.float32)
    noisy_image = image.astype(np.float32) + noise
    return np.clip(noisy_image, 0, 255).astype(np.uint8)

def add_salt_pepper_noise(image, amount=0.05):
    noisy = image.copy()
    num_salt = np.ceil(amount * image.size * 0.5).astype(int)
    num_pepper = np.ceil(amount * image.size * 0.5).astype(int)
    coords = [np.random.randint(0, i, num_salt) for i in image.shape[:2]]
    noisy[coords[0], coords[1]] = 255
    coords = [np.random.randint(0, i, num_pepper) for i in image.shape[:2]]
    noisy[coords[0], coords[1]] = 0
    return noisy

def random_rotation(image):
    angle = random.choice([90, 180, 270])
    return cv2.rotate(image, {90: cv2.ROTATE_90_CLOCKWISE,
                              180: cv2.ROTATE_180,
                              270: cv2.ROTATE_90_COUNTERCLOCKWISE}[angle])

def random_flip(image):
    if random.random() > 0.5:
        return cv2.flip(image, 1)
    return image

def adjust_brightness_contrast(image, brightness=30, contrast=30):
    b = random.randint(-brightness, brightness)
    c = random.randint(-contrast, contrast)
    return cv2.convertScaleAbs(image, alpha=1 + c / 127.0, beta=b)

def random_blur(image):
    if random.random() > 0.5:
        ksize = random.choice([3, 5])
        return cv2.GaussianBlur(image, (ksize, ksize), 0)
    return image

def augment_image(image):
    image = random_flip(image)
    image = random_rotation(image)
    image = adjust_brightness_contrast(image, brightness=15, contrast=15)
    image = random_blur(image)
    return image

# 遍历所有子目录和文件
for root, dirs, files in os.walk(input_folder):
    for file in files:
        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            input_path = os.path.join(root, file)
            rel_path = os.path.relpath(root, input_folder)  # 相对路径
            save_dir = os.path.join(output_folder, rel_path)
            os.makedirs(save_dir, exist_ok=True)

            image = cv2.imread(input_path)
            if image is None:
                continue

            augmented = augment_image(image)

            # 决定是否加噪声（随机）
            if random.random() < 0.4:
                if random.random() > 0.5:
                    augmented = add_gaussian_noise(augmented, std=5)
                else:
                    augmented = add_salt_pepper_noise(augmented, amount=0.005)

            save_path = os.path.join(save_dir, 'aug_' + file)
            cv2.imwrite(save_path, augmented)

print("已完成：所有子文件夹图像增强（随机加噪）。")
