/* 2352018 大数据 刘彦 */
#include <iostream>
#include <fstream>
//不再允许加入任何头文件，特别是<Windows.h>，查到就是0分甚至是倒扣-20!!!!!
using namespace std;

#include "15-b8-bmp.h"

/***************************************************************************
  函数名称：bitmap(const char* const filename)
  功    能：构造函数，读取指定的 BMP 图像文件
  输入参数：const char* const filename - 文件名
  返 回 值：无
  说    明：读取 BMP 文件并解析图像信息
***************************************************************************/
bitmap::bitmap(const char* const filename) 
{
    // 打开文件
    ifstream in(filename, ios::in | ios::binary);
    if (!in.is_open()) 
    {
        cout << "打开文件失败！" << endl;
        exit(-1);
    }

    // 读文件头有效内容
    in.seekg(2, ios::cur);  // 跳过文件标识符
    in.read((char*)&filesize, sizeof(int));
    in.seekg(4, ios::cur);   // 跳过保留字节
    in.read((char*)&bfoffBits, sizeof(unsigned long));  // 位图数据偏移

    // 读位图信息头有效内容
    in.seekg(4, ios::cur);   // 跳过信息头
    in.read((char*)&b_width, sizeof(int));   // 宽度
    in.read((char*)&b_height, sizeof(int));  // 高度
    in.seekg(2, ios::cur);   // 跳过色彩深度信息
    in.read((char*)&biBitCount, sizeof(short));  // 位深
    in.seekg(16, ios::cur);  // 跳过其他未用信息
    in.read((char*)&biClrUsed, sizeof(int));   // 调色板颜色数

    if (biClrUsed == 0)
        biClrUsed = (1 << biBitCount);  // 默认使用的颜色数

    // 读取调色板（如果有）
    in.seekg(4, ios::cur);   // 跳过保留字节
    if (biBitCount <= 8) // 如果是8位或以下，读取调色板
    {   
        color_board = new unsigned char[biClrUsed][4];
        memset(color_board, 0, sizeof(color_board));  // 初始化
        in.read((char*)color_board, biClrUsed * 4);  // 读取调色板数据
    }
    else 
        color_board = NULL;

    // 读取位图数据
    bmp_data = new unsigned char[filesize];
    in.read((char*)bmp_data, filesize - bfoffBits);  // 读取位图数据部分
    in.close();  // 关闭文件
}


/***************************************************************************
  函数名称：~bitmap()
  功    能：析构函数，释放内存
  输入参数：无
  返 回 值：无
  说    明：释放内存
***************************************************************************/
bitmap::~bitmap()
{
    delete[] color_board;
    delete[] bmp_data;
}

/***************************************************************************
  函数名称：get_pixel(int row, int col) const
  功    能：根据坐标获取像素颜色
  输入参数：row - 行，col - 列
  返 回 值：像素的 RGB 颜色
  说    明：返回图像中指定位置的颜色
***************************************************************************/
unsigned int bitmap::get_pixel(int row, int col) const 
{
    // 调整行号以适应 BMP 的坐标系统（从底部开始）
    int b_row = (b_height) > 0 ? (b_height - row - 1) : row;
    int b_col = col;
    int RowByteCnt = (((b_width * biBitCount) + 31) >> 5) << 2; // 每行的字节数

    if (biBitCount <= 8) // 8位及以下图像
    {  
        // 每个字节对应的像素数
        int PixelPerByte = 8 / biBitCount;
        // 计算字节偏移
        int pixelOffset = (b_row * RowByteCnt) + b_col / PixelPerByte;
        // 获取调色板的颜色索引
        unsigned int index = bmp_data[pixelOffset];
        // 计算当前像素索引的位偏移量
        int indexOffset = (PixelPerByte - 1 - b_col % PixelPerByte) * biBitCount;
        index >>= indexOffset;
        index = index % biClrUsed;  // 确保索引不会越界
        // 从调色板中获取颜色
        unsigned char B = color_board[index][0];
        unsigned char G = color_board[index][1];
        unsigned char R = color_board[index][2];
        return my_RGB(R, G, B);  // 使用宏返回RGB颜色值
    }
    else // 24位或32位图像
    {  
        // 每个像素的字节数
        int bytesPerPixel = biBitCount / 8;
        // 计算字节偏移
        int pixelOffset = (b_row * RowByteCnt) + bytesPerPixel * b_col;

        // 对于24/32位图像，BMP的默认存储顺序为BGR
        unsigned char B = bmp_data[pixelOffset];
        unsigned char G = bmp_data[pixelOffset + 1];
        unsigned char R = bmp_data[pixelOffset + 2];

        return my_RGB(R, G, B);  // 使用宏返回RGB颜色值
    }
}

/***************************************************************************
  函数名称：show
  功    能：根据给定的坐标、角度、是否镜像等信息，显示图像
  输入参数：top_left_x - 左上角 x 坐标，top_left_y - 左上角 y 坐标
            angle - 旋转角度，is_mirror - 是否镜像
            draw_point - 绘制单个点的函数指针
  返 回 值：显示图像的像素数
  说    明：根据给定的参数绘制图像，可以旋转、镜像。
***************************************************************************/
int bitmap::show(const int top_left_x, const int top_left_y, const int angle, const bool is_mirror,
    void (*draw_point)(const int x, const int y, const unsigned char red, const unsigned char green, const unsigned char blue)) const
{
    // 根据旋转和镜像的参数，绘制图像的每个像素
    int pixel_count = 0;
    for (int row = 0; row < b_height; row++) 
    {
        for (int col = 0; col < b_width; col++)
        {
            unsigned int color = get_pixel(row, col);
            unsigned char R = (color >> 16) & 0xFF;
            unsigned char G = (color >> 8) & 0xFF;
            unsigned char B = color & 0xFF;
            int new_x = top_left_x + col;
            int new_y = top_left_y + row;

            // 处理镜像和旋转
            if (is_mirror) 
                new_x = top_left_x + (b_width - col - 1);
            if (angle == 90) 
            {
                int temp = new_x;
                new_x = top_left_y + (b_width - new_y - 1);
                new_y = top_left_x + temp;
            }
            else if (angle == 180) 
            {
                new_x = top_left_x + (b_width - new_x - 1);
                new_y = top_left_y + (b_height - new_y - 1);
            }
            else if (angle == 270) 
            {
                int temp = new_x;
                new_x = top_left_x + (b_height - new_y - 1);
                new_y = top_left_y + temp;
            }

            draw_point(new_x, new_y, R, G, B);
            pixel_count++;
        }
    }
    return pixel_count;
}