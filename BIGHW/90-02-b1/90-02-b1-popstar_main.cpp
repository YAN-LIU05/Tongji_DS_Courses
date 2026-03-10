/* 2352018 大数据 刘彦 */
#include <iostream>
#include <windows.h>
#include <conio.h>
#include "../include/cmd_console_tools.h"
#include "../include/bighw.h"
#include "90-02-b1-popstar.h"
using namespace std;

int main()
{
	cct_setconsoleborder(120, 40, 120, 9000);
	cct_setfontsize("新宋体", 16);
	int x, y;
	while (1)
	{
		int choice = all_menu('A');
		int choice0;
		if (choice >= 'a' && choice <= 'z')
			choice0 = choice - 'a' + 'A';
		else
			choice0 = choice;
		if (choice == 'Q' || choice == 'q')
		{
			cct_gotoxy(0, 30);
			break;
		}
		else
		{
			Sleep(200);
			cct_cls();
			//填充函数
			if ((choice >= 'A' && choice <= 'G') || (choice >= 'a' && choice <= 'g'))
				popstar_base_all(choice0);
			cct_setcursor(CURSOR_VISIBLE_NORMAL);
			cout << "本小题结束，请输入End继续...";
			cct_getxy(x, y);
			char input[MAX_LENGTH] = { 0 };
			int index = 0; // 用于跟踪数组中的当前位置
			bool end = false;

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
					end = true;
				else if (ch == '\r')
				{
					cout << endl;

					cout << "输入错误，请重新输入";
					index = 0;
					input[0] = '\0';
					cct_gotoxy(x, y);
					for (int i = 1; i < 10; i++)
						cout << " ";
					cct_gotoxy(x, y);
				}
			}
			cct_setconsoleborder(120, 40, 120, 9000);
			cct_setfontsize("新宋体", 16);
			cct_cls();
		}
	}
	
	return 0;

}
