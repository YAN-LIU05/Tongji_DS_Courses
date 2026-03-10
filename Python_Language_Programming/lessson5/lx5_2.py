import cv2
import os

def cartoonise(picture_name):
    # 定义缩减像素采样和双边滤波的次数
    num_down = 2
    num_bilateral = 7

    # 读取图片
    img_rgb = cv2.imread(picture_name)

    # 用高斯金字塔降低取样
    img_color = img_rgb
    for _ in range(num_down):
        img_color = cv2.pyrDown(img_color)

    # 重复使用小的双边滤波代替一个大的滤波
    for _ in range(num_bilateral):
        img_color = cv2.bilateralFilter(img_color, d=9, sigmaColor=9, sigmaSpace=7)

    # 升采样图片到原始大小
    for _ in range(num_down):
        img_color = cv2.pyrUp(img_color)

    # 转换为灰度并且使其产生中等的模糊
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    img_blur = cv2.medianBlur(img_gray, 7)

    # 检测到边缘并且增强其效果
    img_edge = cv2.adaptiveThreshold(img_blur, 255,
                                     cv2.ADAPTIVE_THRESH_MEAN_C,
                                     cv2.THRESH_BINARY,
                                     blockSize=9,
                                     C=2)

    # 转换回彩色图像
    img_edge = cv2.cvtColor(img_edge, cv2.COLOR_GRAY2RGB)

    img_resize = cv2.resize(img_color, (img_rgb.shape[1], img_rgb.shape[0]))

    # 位运算得到卡通效果
    img_cartoon = cv2.bitwise_and(img_resize, img_edge)

    # 保存转换后的图片，确保文件名正确
    _, file_extension = os.path.splitext(picture_name)
    imgOutput_FileName = picture_name.replace(file_extension, "cartoon" + file_extension)
    cv2.imwrite(imgOutput_FileName, img_cartoon)

if __name__ == '__main__':
    # 获取当前工作目录并拼接图片文件名
    s = os.path.join(os.getcwd(), "2352018.jpg")
    cartoonise(s)