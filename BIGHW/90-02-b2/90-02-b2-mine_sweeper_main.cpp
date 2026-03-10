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
#include "90-02-b2-mine_sweeper.h"

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
	CONSOLE_GRAPHICS_INFO MineSweeper_CGI; //声明一个CGI变量
	int choice;
	
    while (1)
    {
        cct_setconsoleborder(120, 40, 120, 9000);
        cct_setfontsize("新宋体", 16);
        while (1)
        {
            cout << R"(请输入扫雷游戏的等级(数字), 初级\中级\高级(1\2\3)  )";
            cin >> choice;
            if (choice >= 1 && choice <= 3)
                break;
            else if (!cin.good())
            {
                cin.clear();
                cin.ignore(INT_MAX, '\n');
            }
        }
       
        cct_cls();

        mine_map_all(&MineSweeper_CGI, choice);
        Sleep(3000);
        gmw_status_line(&MineSweeper_CGI, LOWER_STATUS_LINE, "按回车继续", NULL);
        if (_getch() == '\r')
            break;
        else
            continue;
    }
    
}






















