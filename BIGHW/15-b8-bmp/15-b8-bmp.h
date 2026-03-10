/* 2352018 大数据 刘彦 */
#pragma once

//不允许加入任何头文件，特别是<Windows.h>，查到就是0分甚至是倒扣-20 ！！！

//自行查阅相关资料，了解下面这几个预编译命令的作用，看能否给你的作业带来方便！！！
//#pragma pack(show) //以警告信息的形式显示当前字节对齐的值
//#pragma pack(push) //将当前字节对齐值压入编译器栈的栈顶
//#pragma pack(push, 4) //将当前字节对齐值压入编译器栈的栈顶，然后再将4设置当前值
//#pragma pack(pop)  //将编译器栈栈顶的字节对齐值弹出并设置为当前值
//#pragma pack() //不带参数是恢复默认值

//允许定义其它需要的结构体（类）、常量、常变量等
#define my_RGB(r, g, b) ((unsigned int)(((b) & 0xFF) | (((g) & 0xFF) << 8) | (((r) & 0xFF) << 16))) 

class bitmap {
private:
    int b_width;               // 图像宽度
    int b_height;              // 图像高度
    short biBitCount;          // 位深
    int biClrUsed;             // 调色板颜色数
    unsigned long bfoffBits;   // 位图数据偏移
    int filesize;              // 文件大小
    unsigned char* bmp_data;   // 位图数据
    unsigned char(*color_board)[4]; // 调色板数据

    // 内部函数来获取像素颜色
    unsigned int get_pixel(int row, int col) const;


public:
    bitmap(const char* const filename);
    ~bitmap();
    int show(const int top_left_x, const int top_left_y, const int angle, const bool is_mirror,
        void (*draw_point)(const int x, const int y, const unsigned char red, const unsigned char green, const unsigned char blue)) const;
};
