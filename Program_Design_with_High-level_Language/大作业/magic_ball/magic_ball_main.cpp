/* 2352018 信06 刘彦 */
#include <iostream>
#include <conio.h>
#include "cmd_console_tools.h"
#include "magic_ball.h"
using namespace std;

#define MAX_LENGTH 256

/***************************************************************************
  函数名称：main
  功    能：调用函数
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
int main()
{
	/* demo中首先执行此句，将cmd窗口设置为40行x120列（缓冲区宽度120列，行数9000行，即cmd窗口右侧带有垂直滚动杆）*/
	cct_setconsoleborder(120, 40, 120, 9000);
	cct_setfontsize("新宋体",  16);
	int x, y;
	while (1)
	{
		int choice = magic_menu();
		if (choice == 0)
		{
			cct_gotoxy(0, 30);
			break;
		}
		else
		{
			cct_cls();
			//填充函数
			if (choice >= 1 && choice <= 9)
				ball_base_all(choice);
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
					if (choice <= 3 && choice >= 1)
						cout << "输入错误，请重新输入";
					if (choice == 4 || choice == 5)
						cout << "本小题结束，请输入End继续...";
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