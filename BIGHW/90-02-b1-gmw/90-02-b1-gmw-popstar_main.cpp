/* 2352018 大数据 刘彦 */
#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <cstdlib> 
#include <ctime> 
#include <windows.h>
#include <conio.h>
#include <iomanip>
#include "../include/cmd_console_tools.h"
#include "../include/cmd_gmw_tools.h"
#include "../include/bighw.h"
#include "90-02-b1-gmw-popstar.h"

using namespace std;


/***************************************************************************
  函数名称：main
  功    能：汇总函数
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
int main()
{
    CONSOLE_GRAPHICS_INFO PopStar_CGI; //声明一个CGI变量
    int rows, cols;
    //int row0, col0;
    //int x, y;
    int count1 = 0;
    int score = 0;
    int total = 0;
    char input[MAX_LENGTH] = { 0 };
    int index = 0; // 用于跟踪数组中的当前位置
    bool end = false;
    // 输入验证
    while (1)
    {
        cct_setconsoleborder(120, 40, 120, 9000);
        cct_setfontsize("新宋体", 16);
        cout << "请输入行数(8-10)：" << endl;
        cin >> rows;

        if (rows >= MIN_ROWS && rows <= MAX_ROWS)
            break;
        else if (!cin.good())
        {
            cin.clear();
            cin.ignore(INT_MAX, '\n');
        }
    }
    while (1)
    {
        cout << "请输入列数(8-10)：" << endl;
        cin >> cols;

        if (cols >= MIN_COLS && cols <= MAX_COLS)
            break;
        else if (!cin.good())
        {
            cin.clear();
            cin.ignore(INT_MAX, '\n');
        }
    }

    srand(static_cast<unsigned int>(time(nullptr)));
    int array[MAX_ROWS][MAX_COLS];   //填充数组为随机数
    bool one_round = 1;
    fill_array(array, rows, cols, 2);
    draw_map(rows, cols, 1, array, 'G', &PopStar_CGI);
    gmw_status_line(&PopStar_CGI, LOWER_STATUS_LINE, "本小题结束，请输入End继续... ", "");
    cout << endl;
    int x = 0, y = 0;


    while (!end)
    {
        char ch = _getch();
        if (index < MAX_LENGTH - 1)
        {
            cout << ch;
            input[index++] = ch;   //将字符添加到输入数组中
            input[index] = '\0';   //确保字符串以空字符结尾
        }
        if (tj_strcasecmp(input, "End\r") == 0)	  //检查是否输入了完整的"End\r"
        {
            end = true;
            cout << endl;
        }

        else if (ch == '\r')
        {
            gmw_status_line(&PopStar_CGI, LOWER_STATUS_LINE, "输入错误，请重新输入", "");
            cout << endl;
            cct_getxy(x, y);
            cout << "         ";
            cct_gotoxy(x, y);
            index = 0;
            input[0] = '\0';
            
        }
    }
   
    return 0;
}

