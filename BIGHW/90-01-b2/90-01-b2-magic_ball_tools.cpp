/* 2352018 大数据 刘彦 */
#include <iostream>
#include <conio.h>
#include "../include/cmd_console_tools.h"
#include "../include/bighw.h"
#include "90-01-b2-magic_ball.h"
using namespace std;


/***************************************************************************
  函数名称：print_mark
  功    能：打印初始可消除项
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void print_mark(int rows, int cols, int array[MIN_ROWS][MAX_ROWS])
{
    cout << endl;
    cout << "初始可消除项（不同色标识）：" << endl;
    cout << "  | ";
    for (int j = 0; j < cols; ++j)
        cout << " " << j + 1 << " ";
    cout << endl;
    cout << "--+-";;
    for (int i = 0; i < cols; ++i)
        cout << "---";
    cout << endl;
    for (int i = 0; i < rows; ++i)
    {
        cout << static_cast<char>('A' + i) << " | ";
        for (int j = 0; j < cols; ++j)
        {
            // 检查并标记可消除项
            if (base_check0(array, i, j, rows, cols))
            {
                cout << " ";
                cct_setcolor(COLOR_HYELLOW, COLOR_HBLUE);
                cout << array[i][j];
                cct_setcolor(COLOR_BLACK, COLOR_WHITE);// 重置颜色
                cout << " ";
            }
            else
                cout << " " << array[i][j] << " ";
        }
        cout << endl;
    }
    cout << endl;
}

/***************************************************************************
  函数名称：print_tips
  功    能：打印提示项
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void print_tips(int rows, int cols, int array[MIN_ROWS][MAX_ROWS])
{
    int directions[4][2] = { {-1, 0}, {1, 0}, {0, -1}, {0, 1} };   //方向数组
    cout << endl;
    cout << "可选择的消除提示（不同色标识）：" << endl;
    cout << "  | ";
    for (int j = 0; j < cols; ++j)
        cout << " " << j + 1 << " ";
    cout << endl;
    cout << "--+-";;
    for (int i = 0; i < cols; ++i)
        cout << "---";
    cout << endl;
    for (int i = 0; i < rows; ++i)
    {
        cout << static_cast<char>('A' + i) << " | ";
        for (int j = 0; j < cols; ++j)
        {
            // 检查并标记可消除项
            if (base_check2(array, directions, i, j, rows, cols))
            {
                cout << " ";
                cct_setcolor(COLOR_HYELLOW, COLOR_HBLUE);
                cout << array[i][j];
                cct_setcolor(COLOR_BLACK, COLOR_WHITE);// 重置颜色
                cout << " ";
            }
            else
                cout << " " << array[i][j] << " ";
        }
        cout << endl;
    }
}

