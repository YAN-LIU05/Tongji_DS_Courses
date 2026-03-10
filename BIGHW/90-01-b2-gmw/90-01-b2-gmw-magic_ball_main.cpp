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
#include "90-01-b2-gmw-magic_ball.h"

using namespace std;

/***************************************************************************
  函数名称：main
  功    能：调用函数
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
int main()
{
    int rows, cols;
    char input[MAX_LENGTH] = { 0 };
    bool end = false;
    int index = 0; // 用于跟踪数组中的当前位置
    CONSOLE_GRAPHICS_INFO pMagicBall_CGI;
	cct_setconsoleborder(120, 40, 120, 9000);
	cct_setfontsize("新宋体", 16);
    while (1)
    {
        cout << "请输入行数(5-9)：" << endl;
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
        cout << "请输入列数(5-9)：" << endl;
        cin >> cols;

        if (cols >= MIN_COLS && cols <= MAX_COLS)
            break;
        else if (!cin.good())
        {
            cin.clear();
            cin.ignore(INT_MAX, '\n');
        }
    }
    ball_base_all(&pMagicBall_CGI, rows, cols);

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
            gmw_status_line(&pMagicBall_CGI, LOWER_STATUS_LINE, "输入错误，请重新输入", "");
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