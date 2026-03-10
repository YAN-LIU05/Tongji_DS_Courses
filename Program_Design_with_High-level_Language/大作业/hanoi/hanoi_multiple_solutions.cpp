/* 2352018 信06 刘彦 */
#include <iostream>
#include <iomanip>
#include <windows.h>
#include <conio.h>
#include "cmd_console_tools.h"
#include "hanoi.h"
using namespace std;

#define LOC_X_A 11
#define LOC_X_B 21
#define LOC_X_C 31
#define LOC_Y_4 14
#define LOC_Y_8 34
#define LOC_ROW_X 0
#define LOC_ROW_Y 19
#define LOC_COLUMN 10
#define LOC_LINE_X 10
#define LOC_LINE_Y 13
#define LOC_ENTER_X 0
#define LOC_ENTER_Y 30
#define BOTTOM_WIDTH 23
#define BOTTOM_X 1
#define BOTTOM_Y 15
#define STICK_WIDTH 1
#define LOC_TOWER 32
#define TIME_SLEEP 45 
#define X_9 60
#define Y_9 35
#define MAX_9 20

/* ----------------------------------------------------------------------------------

     本文件功能：
    1、存放被 hanoi_main.cpp 中根据菜单返回值调用的各菜单项对应的执行函数

     本文件要求：
    1、不允许定义外部全局变量（const及#define不在限制范围内）
    2、允许定义静态全局变量（具体需要的数量不要超过文档显示，全局变量的使用准则是：少用、慎用、能不用尽量不用）
    3、静态局部变量的数量不限制，但使用准则也是：少用、慎用、能不用尽量不用
    4、按需加入系统头文件、自定义头文件、命名空间等

   ----------------------------------------------------------------------------------- */
int hanoi0[3][10];
int top[3];
int Count = 0;// 移动次数计数器
int speed;

/***************************************************************************
  函数名称：capital
  功    能：转大写
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
char capital(char x)
{
    if (x == 'a' || x == 'A')
        x = 'A';
    if (x == 'B' || x == 'b')
        x = 'B';
    if (x == 'c' || x == 'C')
        x = 'C';
    return x;
}

/***************************************************************************
  函数名称：my_sleep
  功    能：控制时间
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void my_sleep()
{
    switch (speed)
    {
        case 1:
            Sleep(50);
            break;
        case 2:
            Sleep(40);
            break;
        case 3:
            Sleep(30);
            break;
        case 4:
            Sleep(20);
            break;
        case 5:
            Sleep(10);
            break;
    }
}

/***************************************************************************
  函数名称：draw_tower
  功    能：打印底座，柱子和盘
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void draw_tower(int n, int src, int choice)
{
    int i, j, k, m;
    int bottom, stick;   //打印底座和柱子
    int color1, color2;   //盘和背景的颜色
    int startX, startY;   //打印盘的位置
    for (i = 0; i < 3; i++)   //打印底座
    {
        bottom = BOTTOM_X + LOC_TOWER * i;
        Sleep(TIME_SLEEP);
        cct_showstr(bottom, BOTTOM_Y, " ", COLOR_HYELLOW, COLOR_HYELLOW, BOTTOM_WIDTH);
    }

    for (j = 14; j > 1; j--)   //打印柱子
    {
        for (k = 0; k < 3; k++)
        {
            stick = BOTTOM_Y + LOC_TOWER * k - BOTTOM_X - 2;
            Sleep(45);
            cct_showch(stick, j + 1, ' ', COLOR_HYELLOW, COLOR_HYELLOW, STICK_WIDTH);
        }
    }
    // 将文本颜色设置为黑色，背景颜色设置为白色
    cct_setcolor(COLOR_BLACK, COLOR_WHITE);

    if (choice == 6 || choice == 7 || choice == 8 || choice == 9)
    {
        int num = src - 'A';

        // 循环绘制动态矩形
        for (m = n; m >= 1; m--)
        {
            Sleep(TIME_SLEEP);

            // 计算当前迭代的颜色值
            color1 = COLOR_BLUE + m;
            color2 = COLOR_BLUE + m;

            // 计算当前迭代的位置
            startX = LOC_LINE_X + LOC_TOWER * num - m + 2;
            startY = LOC_LINE_Y - n + m + 1;
            cct_showch(startX, startY, ' ', color1, color2, 1 + 2 * m);
        }
        // 将文本颜色设置为黑色，背景颜色设置为白色
        cct_setcolor(COLOR_BLACK, COLOR_WHITE);
    }
}

/***************************************************************************
  函数名称：draw_move
  功    能：盘移动时的辅助函数1
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void draw_move(char src, char x, int i)
{
    int height = init_plate_height(src);
    int width = init_plate_width(src);
    int loc_x = (x - 'A') * LOC_TOWER + (BOTTOM_WIDTH + BOTTOM_X - width + 1) / 2;
    int color = init_plate_color(src);

    cct_showch((x - 'A') * LOC_TOWER + 1, i, ' ', COLOR_BLACK, COLOR_WHITE, BOTTOM_WIDTH);
    if (i > 2 && i < 15)   //打印柱
        cct_showch((x - 'A') * LOC_TOWER + (BOTTOM_WIDTH + BOTTOM_X) / 2, i, ' ', COLOR_HYELLOW, COLOR_HYELLOW, STICK_WIDTH);
    //在屏幕上的特定位置绘制一个盘
    cct_showch(loc_x, i + 1, ' ', COLOR_BLACK + color, COLOR_BLACK + color, width);
    height = i - 1;
}

/***************************************************************************
  函数名称：drawCharacter
  功    能：盘移动时的辅助函数2
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void drawCharacter(int x, int y, int flag, int color, int width)
{
    cct_showch(x, y, ' ', COLOR_BLACK, COLOR_WHITE, width);

    // 根据水平距离的值决定绘制颜色字符的位置
    int offset = (flag > 0) ? 1 : -1;
    int color0 = COLOR_BLACK + color;

    // 绘制具有特定颜色的字符
    cct_showch(x + offset, y, ' ', color0, color0, width);
}


/***************************************************************************
  函数名称：printTower1
  功    能：打印数组第一列
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void printTower1(int tower[], char label)
{
    cout << label << ":";
    for (int i = 0; i < 10; ++i)
    {
        if (hanoi0[0][i] == 0)
        {
            cout << "  "; // 两个空格表示没有盘
        }
        else
        {
            cout << setw(2) << tower[i];
        }
    }
    cout << " ";
}

/***************************************************************************
  函数名称：printTower2
  功    能：打印数组第二列
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void printTower2(int tower[], char label)
{
    cout << label << ":";
    for (int i = 0; i < 10; ++i)
    {
        if (hanoi0[1][i] == 0)
        {
            cout << "  "; // 两个空格表示没有盘
        }
        else
        {
            cout << setw(2) << tower[i];
        }
    }
    cout << " ";
}

/***************************************************************************
  函数名称：printTower3
  功    能：打印数组第三列
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void printTower3(int tower[], char label)
{
    cout << label << ":";
    for (int i = 0; i < 10; ++i)
    {
        if (hanoi0[2][i] == 0)
        {
            cout << "  "; // 两个空格表示没有盘
        }
        else
        {
            cout << setw(2) << tower[i];
        }
    }
    cout << " ";
}

/***************************************************************************
  函数名称：print
  功    能：打印数组
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void print()
{
    printTower1(hanoi0[0], 'A');
    printTower2(hanoi0[1], 'B');
    printTower3(hanoi0[2], 'C');
}

/***************************************************************************
  函数名称：moveA
  功    能：移动数组A
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void moveA(char dst)
{
    int a;
    a = hanoi0[0][--top[0]];
    hanoi0[0][top[0]] = 0;
    if (dst == 'B')
    {
        hanoi0[1][top[1]++] = a;
    }
    if (dst == 'C')
    {
        hanoi0[2][top[2]++] = a;
    }
}

/***************************************************************************
  函数名称：moveB
  功    能：移动数组B
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void moveB(char dst)
{
    int b;
    b = hanoi0[1][--top[1]];
    hanoi0[1][top[1]] = 0;
    if (dst == 'A')
    {
        hanoi0[0][top[0]++] = b;
    }
    if (dst == 'C')
    {
        hanoi0[2][top[2]++] = b;
    }
}

/***************************************************************************
  函数名称：moveC
  功    能：移动数组C
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void moveC(char dst)
{
    int c;
    c = hanoi0[2][--top[2]];
    hanoi0[2][top[2]] = 0;
    if (dst == 'A')
    {
        hanoi0[0][top[0]++] = c;
    }
    if (dst == 'B')
    {
        hanoi0[1][top[1]++] = c;
    }
}

/***************************************************************************
  函数名称：move
  功    能：移动数组
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void move(char src, char dst)
{
    if (src == 'A')
        moveA(dst);
    if (src == 'B')
        moveB(dst);
    if (src == 'C')
        moveC(dst);
}

/***************************************************************************
  函数名称：move_plate
  功    能：移动盘子
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void move_plate(char src, char dst)
{
    int height = init_plate_height(src);
    int width = init_plate_width(src);
    int loc_x = (src - 'A') * LOC_TOWER + (BOTTOM_WIDTH + BOTTOM_X - width + 1) / 2;
    int color = init_plate_color(src);
    int loc_y = init_plate_dst(dst);
    int flag = (dst - src) * LOC_TOWER;
    int i = height, j = height;
    //绘制盘
    for (; i > 1; i--) 
    {
        Sleep(TIME_SLEEP);
        cct_showch((src - 'A') * 32 + 1, i, ' ', COLOR_BLACK, COLOR_WHITE, BOTTOM_WIDTH);
        if (i > 2 && i < 15)   //打印柱
            cct_showch((src - 'A') * LOC_TOWER + (BOTTOM_WIDTH + BOTTOM_X) / 2, i, ' ', COLOR_HYELLOW, COLOR_HYELLOW, STICK_WIDTH);
        //在屏幕上的特定位置绘制一个盘
        cct_showch(loc_x, i - 1, ' ', COLOR_BLACK + color, COLOR_BLACK + color, width);
        height = i - 1;
    }
    i = height;
    //平移盘
    while (1)
    {
        Sleep(TIME_SLEEP);
        cct_showch(loc_x, height, ' ', COLOR_BLACK, COLOR_WHITE, width);
        drawCharacter(loc_x, height, flag, color, width);

        // 更新x的位置
        loc_x += (flag > 0) ? 1 : (flag < 0) ? -1 : 0;

        // 检查是否达到停止条件
        int locate = flag + (src - 'A') * LOC_TOWER + (BOTTOM_WIDTH + BOTTOM_X - width + 1) / 2;
        if (loc_x == locate)
            break;
    }
    //降落盘
    j = height;
    while (j < loc_y)
    {
        Sleep(TIME_SLEEP);
        draw_move(src, dst, j);
        j++;
    }
    cct_setcolor(COLOR_BLACK, COLOR_WHITE);
}

/***************************************************************************
  函数名称：print_all
  功    能：打印
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void print_all(int n, char src, char tmp, char dst, int choice)
{
    char dst_7 = 0;
    switch (choice)
    {
        case 1:
            print_line(n, src, tmp, dst, 1);
            break;
        case 2:
            print_line(n, src, tmp, dst, 2);
            break;
        case 3:
            print_row(n, src, tmp, dst, 3);
            break;
        case 4:
            switch (speed)
            {
                case 0:
                    if (_getch() == 13)   //按回车单步演示,回车的ASCII码的值为13
                    {
                        print_row(n, src, tmp, dst, 4);
                        print_column_base(4);
                        print_column_tower(4);
                    }
                    break;
                case 1:
                    Sleep(250);
                    print_row(n, src, tmp, dst, 4);
                    print_column_base(4);
                    print_column_tower(4);
                    break;
                case 2:
                    Sleep(200);
                    print_row(n, src, tmp, dst, 4);
                    print_column_base(4);
                    print_column_tower(4);
                    break;
                case 3:
                    Sleep(150);
                    print_row(n, src, tmp, dst, 4);
                    print_column_base(4);
                    print_column_tower(4);
                    break;
                case 4:
                    Sleep(100);
                    print_row(n, src, tmp, dst, 4);
                    print_column_base(4);
                    print_column_tower(4);
                    break;
                case 5:
                    Sleep(50);
                    print_row(n, src, tmp, dst, 4);
                    print_column_base(4);
                    print_column_tower(4);
                    break;
            }
            break;
        case 7:
            dst_7 = hanoi_move(n, src, tmp, dst);
            move_plate(src, dst_7);
            break;
        case 8:
            switch (speed)
            {
                case 0:
                    if (_getch() == 13)
                    {
                        print_row(n, src, tmp, dst, 8);
                        print_column_base(8);
                        print_column_tower(8);
                        move(dst, src);
                        move_plate(src, dst);
                        move(src, dst);
                    }
                    break;//按回车单步演示,回车的ASCII码的值为13
                case 1:
                    Sleep(250);
                    print_row(n, src, tmp, dst, 8);
                    print_column_base(8);
                    print_column_tower(8);
                    move(dst, src);
                    move_plate(src, dst);
                    move(src, dst);
                    break;
                case 2:
                    Sleep(200);
                    print_row(n, src, tmp, dst, 8);
                    print_column_base(8);
                    print_column_tower(8);
                    move(dst, src);
                    move_plate(src, dst);
                    move(src, dst);
                    break;
                case 3:
                    Sleep(150);
                    print_row(n, src, tmp, dst, 8);
                    print_column_base(8);
                    print_column_tower(8);
                    move(dst, src);
                    move_plate(src, dst);
                    move(src, dst);
                    break;
                case 4:
                    Sleep(100);
                    print_row(n, src, tmp, dst, 8);
                    print_column_base(8);
                    print_column_tower(8);
                    move(dst, src);
                    move_plate(src, dst);
                    move(src, dst);
                    break;
                case 5:
                    Sleep(50);
                    print_row(n, src, tmp, dst, 8);
                    print_column_base(8);
                    print_column_tower(8);
                    move(dst, src);
                    move_plate(src, dst);
                    move(src, dst);
                    break;
            }
            break;
        case 9:
            print_row(n, src, tmp, dst, 9);
            print_column_base(9);
            print_column_tower(9);
            move(dst, src);
            move_plate(src, dst);
            move(src, dst);
            break;
    }
}

/***************************************************************************
  函数名称：print_line
  功    能：逐行输出数组
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void print_line(int n, char src, char tmp, char dst, int choice)
{
    switch (choice)
    {
        case 1:
            cout << n << "# " << src << "-->" << dst << endl;
            break;
        case 2:
            cout << "第" << setw(4) << Count << " 步" << "(" << setw(2) << n << "#" << ": " << src << "-->" << dst << ")  " << endl;
            break;
    }
}

/***************************************************************************
  函数名称：print_row
  功    能：横向输出数组
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void print_row(int n, char src, char tmp, char dst, int choice)
{
    switch (choice)
    {
        case 3:
            break;
        case 4:
            cct_gotoxy(LOC_ROW_X, LOC_ROW_Y);
            break;
        case 8:
            cct_gotoxy(LOC_ROW_X, LOC_ROW_Y + 18);
            break;
        case 9:
            cct_gotoxy(LOC_ROW_X, LOC_ROW_Y + 14);
            break;
    }
    cout << "第" << setw(4) << Count << " 步" << "(" << setw(2) << n << ")" << ": " << src << "-->" << dst << " ";
    move(src, dst);
    print();
    cout << endl;
}

/***************************************************************************
  函数名称：print_column_base
  功    能：纵向输出数组的基础结构
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void print_column_base(int choice)
{
    int i;
    cct_gotoxy(0, 0);
    switch (choice)
    {
        case 4:
            for (i = 0; i < 21; i++)
            {
                cout << endl;
            }
            //打印基本结构
            cct_gotoxy(LOC_LINE_X, LOC_LINE_Y);
            for (int j = 0; j < 23; j++)
                cout << "=";
            cct_gotoxy(LOC_X_A, LOC_Y_4);
            cout << "A";
            cct_gotoxy(LOC_X_B, LOC_Y_4);
            cout << "B";
            cct_gotoxy(LOC_X_C, LOC_Y_4);
            cout << "C";
            break;
        case 8:
            for (i = 0; i < 21; i++)
            {
                cout << endl;
            }
            //打印基本结构
            cct_gotoxy(LOC_LINE_X, LOC_LINE_Y + 20);
            for (int j = 0; j < 23; j++)
                cout << "=";
            cct_gotoxy(LOC_X_A, LOC_Y_8);
            cout << "A";
            cct_gotoxy(LOC_X_B, LOC_Y_8);
            cout << "B";
            cct_gotoxy(LOC_X_C, LOC_Y_8);
            cout << "C";
            break;
        case 9:
            for (i = 0; i < 21; i++)
            {
                cout << endl;
            }
            //打印基本结构
            cct_gotoxy(LOC_LINE_X, LOC_LINE_Y + 15);
            for (int j = 0; j < 23; j++)
                cout << "=";
            cct_gotoxy(LOC_X_A, LOC_Y_8 - 5);
            cout << "A";
            cct_gotoxy(LOC_X_B, LOC_Y_8 - 5);
            cout << "B";
            cct_gotoxy(LOC_X_C, LOC_Y_8 - 5);
            cout << "C";
            break;
    }
}

/***************************************************************************
  函数名称：print_column_tower
  功    能：纵向输出数组中的数
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void print_column_tower(int choice)
{
    int i, j, h;

    switch (choice)
    {
        case 4:
            for (i = 0; i < 3; i++)
            {
                h = LOC_Y_4 - 2;
                for (j = 0; j < 10; ++j)
                {
                    cct_gotoxy(LOC_COLUMN * (i + 1), h);
                    if (hanoi0[i][j] == 0)
                    {
                        cout << "  "; // 两个空格表示没有盘
                    }
                    else
                    {
                        cout << setw(2) << hanoi0[i][j];
                    }
                    h--;
                }
                cout << " ";
            }
            break;
        case 8:
            for (i = 0; i < 3; i++)
            {
                h = LOC_Y_8 - 2;
                for (j = 0; j < 10; ++j)
                {
                    cct_gotoxy(LOC_COLUMN * (i + 1), h);
                    if (hanoi0[i][j] == 0)
                    {
                        cout << "  "; // 两个空格表示没有盘
                    }
                    else
                    {
                        cout << setw(2) << hanoi0[i][j];
                    }
                    h--;
                }
                cout << " ";
            }
            break;
        case 9:
            for (i = 0; i < 3; i++)
            {
                h = LOC_Y_8 - 7;
                for (j = 0; j < 10; ++j)
                {
                    cct_gotoxy(LOC_COLUMN * (i + 1), h);
                    if (hanoi0[i][j] == 0)
                    {
                        cout << "  "; // 两个空格表示没有盘
                    }
                    else
                    {
                        cout << setw(2) << hanoi0[i][j];
                    }
                    h--;
                }
                cout << " ";
            }
            break;
    }
}

/***************************************************************************
  函数名称：init
  功    能：初始化
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void init(int n, int src, int choice)
{
    int i;
    if (src == 'A')
    {
        for (i = 0; i < n; i++)
        {
            hanoi0[0][i] = n - i;
        }
        top[0] = n;
    }
    if (src == 'B')
    {
        for (i = 0; i < n; i++)
        {
            hanoi0[1][i] = n - i;
        }
        top[1] = n;
    }
    if (src == 'C')
    {
        for (i = 0; i < n; i++)
        {
            hanoi0[2][i] = n - i;
        }
        top[2] = n;
    }
    if (choice == 3 || choice == 4 || choice == 8 || choice == 9)
    {
        cout << "初始:";   // 打印初始状态
        cout << "                ";
        print();
        cout << endl;
    }
}

/***************************************************************************
  函数名称：init_plate_height
  功    能：初始化盘子高度
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
int init_plate_height(char src)
{
    int height, width;
    height = 0;
    width = 0;
    if (src == 'A')
    {
        height = BOTTOM_Y - top[0];
    }
    if (src == 'B')
    {
        height = BOTTOM_Y - top[1];
    }
    if (src == 'C')
    {
        height = BOTTOM_Y - top[2];
    }

    return height;
}

/***************************************************************************
  函数名称：init_plate_width
  功    能：初始化盘子宽度
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
int init_plate_width(char src)
{
    int width = 0;
    if (src == 'A')
    {
        width = 2 * hanoi0[0][top[0] - 1] + 1;
    }
    if (src == 'B')
    {
        width = 2 * hanoi0[1][top[1] - 1] + 1;
    }
    if (src == 'C')
    {
        width = 2 * hanoi0[2][top[2] - 1] + 1;
    }

    return width;
}

/***************************************************************************
  函数名称：init_plate_color
  功    能：初始化盘子颜色
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
int init_plate_color(char src)
{
    int color = 0;
    if (src == 'A')
    {
        color = hanoi0[0][top[0] - 1];
    }
    if (src == 'B')
    {
        color = hanoi0[1][top[1] - 1];
    }
    if (src == 'C')
    {
        color = hanoi0[2][top[2] - 1];
    }

    return color + 1;
}

/***************************************************************************
  函数名称：init_plate_dst
  功    能：初始化目标柱
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
int init_plate_dst(char dst)
{
    int loc_y = BOTTOM_Y - top[dst - 'A'] - 1;
    return loc_y;
}

/***************************************************************************
  函数名称：speed
  功    能：处理移动速度
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void my_speed()
{
    while (1)
    {
        cout << "请输入移动速度(0-5: 0-按回车单步演示 1-延时最长 5-延时最短) ";
        cin >> speed;
        if (cin.good() && speed >= 0 && speed <= 5)
            break;
        else
        {
            cin.clear();
            cin.ignore(65536, '\n');
        }
    }
}

/***************************************************************************
  函数名称：hanoi_move
  功    能：7
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
char hanoi_move(int n, char src, char tmp, char dst)
{
    char src0 = src;
    char dst0 = dst;
    char tmp0 = tmp;
    int n0 = n;
    // 移动 n-1 个盘子从源柱到中间柱
    while (n0 > 1)
    {
        src0 = tmp0;
        tmp0 = dst0;
        dst0 = src0;
        n0 -= 1;
    }
    // 将最后一个盘子从源柱移动到目标柱
    char result = dst0;

    return result;
}

/***************************************************************************
  函数名称：my_input
  功    能：输入并处理输入错误
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void my_input(int& storey, char& src, char& dst, char& tmp)
{
    cout << endl;
    while (1)
    {
        cout << "请输入汉诺塔的层数(1-10)" << endl;
        cin >> storey;
        if (cin.good() && storey >= 1 && storey <= 10)
        {
            cin.ignore(65536, '\n');
            break;
        }
        else
        {
            cin.clear();
            cin.ignore(65536, '\n');
        }
    }
    while (1)
    {
        cout << "请输入起始柱(A-C)" << endl;
        cin >> src;
        src = capital(src);
        if (cin.good() && (src >= 'A' && src <= 'C'))
        {
            cin.ignore(65536, '\n');
            break;
        }
        else
        {
            cin.clear();
            cin.ignore(65536, '\n');
        }
    }
    while (1)
    {
        cout << "请输入目标柱(A-C)" << endl;
        cin >> dst;
        dst = capital(dst);
        if (dst == src)
        {
            cout << "目标柱(" << dst << ")不能与起始柱(" << src << ")相同" << endl;
            cin.clear();
            cin.ignore(65536, '\n');
        }
        else if (cin.good() == 1 && (dst >= 'A' && dst <= 'C'))
        {
            cin.ignore(65536, '\n');
            break;
        }
        else
        {
            cin.clear();
            cin.ignore(65536, '\n');
        }
    }

    src = capital(src);
    dst = capital(dst);
    if ((src == 'B' && dst == 'C') || (src == 'C' && dst == 'B'))
        tmp = 'A';
    if ((src == 'A' && dst == 'C') || (src == 'C' && dst == 'A'))
        tmp = 'B';
    if ((src == 'A' && dst == 'B') || (src == 'B' && dst == 'A'))
        tmp = 'C';   //确定辅助柱
}

/***************************************************************************
  函数名称：my_input_9
  功    能：输入并处理输入错误
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void getInput(char(&input)[MAX_9])
{
    while (1) 
    {
        int i = 0;
        while (1) 
        {
            input[i] = _getche();
            if (input[i] == 13) 
            {
                input[i] = '\0';
                break;
            }

            if (input[i] < 33 || input[i] > 126) 
            {
                // 检查是否为小写字母，并且与大写字母'A'相差'a' - 'A'
                if (input[i] >= 'a' && input[i] <= 'z' && input[i] - 'a' == 'a' - 'A') 
                {
                    _getche();
                }
                // 将非打印字符替换为字符串结束符
                input[i] = '\0';
                if (i == MAX_9 - 1)
                {
                    i = 0;
                    cct_gotoxy(X_9, Y_9);
                    cout << "                                         ";
                    cct_gotoxy(X_9, Y_9);
                }
                continue;
            }
            i++;
            if (i == MAX_9)
            {
                i = 0;
                cct_gotoxy(X_9, Y_9);
                cout << "                                         ";
                cct_gotoxy(X_9, Y_9);
            }
        }

        for (int i0 = 0; i0 < 2; i0++)
        {
            input[i0] = capital(input[i0]);
        }

        if (i == 2)
            break;
        bool x1 = input[1] >= 'A' && input[1] <= 'C';
        bool x2 = input[0] >= 'A' && input[0] <= 'C';
        if (x1 && x2) 
            break;
        if (input[0] != input[1])
            break;
        if (i == 1 && (input[0] == 'Q' || input[0] == 'q'))   //退出程序
            break;

        cct_gotoxy(X_9, Y_9);
        for (int j = 0; j <= i + 3; j++) 
        {
            cout << " ";
        }
        cct_gotoxy(X_9, Y_9);
    }
}

/***************************************************************************
  函数名称：hanoi_all
  功    能：汇总整个汉诺塔的输出函数
  输入参数：
  返 回 值：
  说    明：根据参数不同而选择不同功能
***************************************************************************/
int hanoi_all(int choice)
{
    char src = 0, dst = 0, tmp = 0;
    int storey = 0;
    if (choice != 0)
    {
        if (choice != 5)
        {
            my_input(storey, src, dst, tmp);
        }
    }
    if (choice == 4 || choice == 8)
    {
        my_speed();
    }

    switch (choice)
    {
        case 1:
            hanoi(storey, src, tmp, dst, 1);
            break;
        case 2:
            hanoi(storey, src, tmp, dst, 2);
            break;
        case 3:
            init(storey, src, 3);
            hanoi(storey, src, tmp, dst, 3);
            break;
        case 4:
            cct_cls();
            cout << "从 " << src << " 移动到 " << dst << "，共 " << storey << " 层，延时设置为 " << speed;
            cct_gotoxy(LOC_ROW_X, LOC_ROW_Y);
            init(storey, src, 4);
            print_column_base(4);
            print_column_tower(4);
            hanoi(storey, src, tmp, dst, 4);
            cct_gotoxy(LOC_ENTER_X, LOC_ENTER_Y);
            break;
        case 5:
            cct_cls();
            draw_tower(storey, src, 5);
            cct_gotoxy(LOC_ENTER_X, LOC_ENTER_Y);
            break;
        case 6:
            cct_cls();
            cout << "从 " << src << " 移动到 " << dst << "，共 " << storey << " 层";
            cct_setcursor(CURSOR_INVISIBLE);
            draw_tower(storey, src, 6);
            cct_gotoxy(LOC_ENTER_X, LOC_ENTER_Y);
            break;
        case 7:
            cct_cls();
            cout << "从 " << src << " 移动到 " << dst << "，共 " << storey << " 层";
            cct_setcursor(CURSOR_INVISIBLE);
            init(storey, src, 7);
            draw_tower(storey, src, 7);
            print_all(storey, src, tmp, dst, 7);
            cct_gotoxy(LOC_ENTER_X, LOC_ENTER_Y);
            break;
        case 8:
            cct_cls();
            cout << "从 " << src << " 移动到 " << dst << "，共 " << storey << " 层，延时设置为 " << speed;
            cct_setcursor(CURSOR_INVISIBLE);
            cct_gotoxy(LOC_ROW_X, LOC_ROW_Y + 18);
            init(storey, src, 8);
            print_column_base(8);
            print_column_tower(8);
            draw_tower(storey, src, 8);
            hanoi(storey, src, tmp, dst, 8);
            cct_gotoxy(LOC_ENTER_X, LOC_ENTER_Y + 18);
            break;
        case 9:
            char input[20];
            cct_cls();
            cout << "从 " << src << " 移动到 " << dst << "，共 " << storey << " 层";
            cct_setcursor(CURSOR_INVISIBLE);
            cct_gotoxy(LOC_ROW_X, LOC_ROW_Y + 18);
            cct_gotoxy(0, Y_9 - 2);
            init(storey, src, 9);
            print_column_base(9);
            print_column_tower(9);
            draw_tower(storey, src, 9);
            cct_gotoxy(0, Y_9);
            cct_setcursor(CURSOR_VISIBLE_NORMAL);
            cout << "请输入移动的柱号(命令形式：AC=A顶端的盘子移动到C，Q=退出) ：";
            while (1)
            {
                getInput(input);
                blank();
                if (input[0] == 'A') 
                {
                    if (top[0] == 0) 
                    {
                        cout << endl;
                        cout << "源柱为空!";
                        blank();
                        continue;
                    }
                }
                if (input[0] == 'B')
                {
                    if (top[1] == 0)
                    {
                        cout << endl;
                        cout << "源柱为空!";
                        blank();
                        continue;
                    }
                }
                if (input[0] == 'C')
                {
                    if (top[2] == 0)
                    {
                        cout << endl;
                        cout << "源柱为空!";
                        blank();
                        continue;
                    }
                }
                Count++;
                int n0 = 0;
                if (input[0] == 'A')
                {
                    n0 = hanoi0[0][top[0] - 1];
                }
                if (input[0] == 'B')
                {
                    n0 = hanoi0[1][top[1] - 1];
                }
                if (input[0] == 'C')
                {
                    n0 = hanoi0[2][top[2] - 1];
                }
                print_all(n0, input[0], tmp, input[1], 9);

                for (int i = 0; i <= 1; i++)
                {
                    cout << " ";
                }
                cct_gotoxy(X_9, Y_9);
                if ((dst == 'A' && top[0] == storey) || (dst == 'B' && top[1] == storey) || (dst == 'C' && top[2] == storey))
                {
                    cout << endl;
                    cout << "游戏结束" << endl;
                    break;
                }
            }
    }
    return 0;
}


/***************************************************************************
  函数名称：blank
  功    能：清空输入
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void blank() 
{
    Sleep(200);
    cct_gotoxy(60, 35);
    cout << "  ";
    cct_gotoxy(0, 36);
    cout << "                                         ";
    cct_gotoxy(0, 37);
    cout << "                                         ";
    cct_gotoxy(60, 35);
}

/***************************************************************************
  函数名称：hanoi
  功    能：汉诺塔递归函数
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void hanoi(int n, char src, char tmp, char dst, int choice)
{
    if (n == 1)
    {
        Count++;
        print_all(n, src, tmp, dst, choice);
    }
    else
    {
        hanoi(n - 1, src, dst, tmp, choice);
        Count++;
        print_all(n, src, tmp, dst, choice);
        hanoi(n - 1, tmp, src, dst, choice);
    }
}