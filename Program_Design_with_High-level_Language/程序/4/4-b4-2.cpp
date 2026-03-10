/* 2352018 信06 刘彦 */
#include <iostream>
#include <cstdio>
#include <conio.h>
#include <time.h>
#include <windows.h>
using namespace std;

const int MAX_X = 69;	//定义*组成的边框的宽度
const int MAX_Y = 17;	//定义*组成的边框的高度

/***************************************************************************
  函数名称：
  功    能：完成与system("cls")一样的功能，但效率高
  输入参数：
  返 回 值：
  说    明：清除整个屏幕缓冲区，不仅仅是可见窗口区域(使用当前颜色)
***************************************************************************/
void cls(const HANDLE hout)
{
	COORD coord = { 0, 0 };
	CONSOLE_SCREEN_BUFFER_INFO binfo; /* to get buffer info */
	DWORD num;

	/* 取当前缓冲区信息 */
	GetConsoleScreenBufferInfo(hout, &binfo);
	/* 填充字符 */
	FillConsoleOutputCharacter(hout, (TCHAR)' ', binfo.dwSize.X * binfo.dwSize.Y, coord, &num);
	/* 填充属性 */
	FillConsoleOutputAttribute(hout, binfo.wAttributes, binfo.dwSize.X * binfo.dwSize.Y, coord, &num);

	/* 光标回到(0,0) */
	SetConsoleCursorPosition(hout, coord);
	return;
}

/***************************************************************************
  函数名称：gotoxy
  功    能：将光标移动到指定位置
  输入参数：HANDLE hout ：输出设备句柄
			int X       ：指定位置的x坐标
			int Y       ：指定位置的y坐标
  返 回 值：无
  说    明：此函数不准修改
***************************************************************************/
void gotoxy(const HANDLE hout, const int X, const int Y)
{
	COORD coord;
	coord.X = X;
	coord.Y = Y;
	SetConsoleCursorPosition(hout, coord);
}

/***************************************************************************
  函数名称：showch
  功    能：在指定位置处打印一个指定的字符
  输入参数：HANDLE hout ：输出设备句柄
			int X       ：指定位置的x坐标
			int Y       ：指定位置的y坐标
			char ch     ：要打印的字符
  返 回 值：无
  说    明：此函数不准修改
***************************************************************************/
void showch(const HANDLE hout, const int X, const int Y, const char ch)
{
	gotoxy(hout, X, Y);
	putchar(ch);
}

/***************************************************************************
  函数名称：init_border
  功    能：显示初始的边框及随机字符
  输入参数：HANDLE hout：输出设备句柄
  返 回 值：无
  说    明：此函数不准修改
***************************************************************************/
void init_border(const HANDLE hout)
{
	gotoxy(hout, 0, 0);	//光标移回左上角(0,0)
	cout << "***********************************************************************" << endl;
	cout << "*                                                                     *" << endl;
	cout << "*                                                                     *" << endl;
	cout << "*                                                                     *" << endl;
	cout << "*                                                                     *" << endl;
	cout << "*                                                                     *" << endl;
	cout << "*                                                                     *" << endl;
	cout << "*                                                                     *" << endl;
	cout << "*                                                                     *" << endl;
	cout << "*                                                                     *" << endl;
	cout << "*                                                                     *" << endl;
	cout << "*                                                                     *" << endl;
	cout << "*                                                                     *" << endl;
	cout << "*                                                                     *" << endl;
	cout << "*                                                                     *" << endl;
	cout << "*                                                                     *" << endl;
	cout << "*                                                                     *" << endl;
	cout << "*                                                                     *" << endl;
	cout << "***********************************************************************" << endl;

	/* 随机显示20个大写字母，字母的值、XY坐标都随机显示
	   rand()函数的功能：随机生成一个在 0-32767 之间的整数
	   思考：在什么情况下，下面这个循环执行生成后，你看到的实际字母个数不足20个？ */
	int i;
	for (i = 0; i < 20; i++)
		showch(hout, rand() % MAX_X + 1, rand() % MAX_Y + 1, 'A' + rand() % 26);

	return;
}

int menu(const HANDLE hout)
{
	int in;
	while (1)
	{
		cout << "1.用I、J、K、L键控制上下左右(大小写均可，边界停止)" << endl;
		cout << "2.用I、J、K、L键控制上下左右(大小写均可，边界回绕)" << endl;
		cout << "3.用箭头键控制上下左右，边界停止" << endl;
		cout << "4.用箭头键控制上下左右，边界回绕" << endl;
		cout << "5.用I、J、K、L键控制上下左右(大小写均可，边界停止，左方向键不可以使用)" << endl;
		cout << "6.用I、J、K、L键控制上下左右(大小写均可，边界回绕，左方向键不可以使用)" << endl;
		cout << "0.退出" << endl;
		cout << "[请选择0-6] ";
		in = _getche();
		if (in < '0' || in >'6')
			cls(hout);
		else
			break;
	}
	return in;
}
void move_by_ijkl(const HANDLE hout, int x)
{
	int m, xl, yl;
	xl = (MAX_X + 1) / 2;
	yl = (MAX_Y + 1) / 2;

	if (x == '1')
	{
		while (1)
		{
			m = _getch();
			if (m == ' ')
			{
				showch(hout, xl, yl, ' ');
				gotoxy(hout, xl, yl);
			}
			if (m == 'Q' || m == 'q')
				break;
			if (m == 'I' || m == 'i')
			{
				if (yl == 1)
					continue;
				else
				{
					yl--;
					gotoxy(hout, xl, yl);
				}
			}
			if (m == 'K' || m == 'k')
			{
				if (yl == 17)
					continue;
				else
				{
					yl++;
					gotoxy(hout, xl, yl);
				}
			}
			if (m == 'J' || m == 'j')
			{
				if (xl == 1)
					continue;
				else
				{
					xl--;
					gotoxy(hout, xl, yl);
				}
			}
			if (m == 'L' || m == 'l')
			{
				if (xl == 69)
					continue;
				else
				{
					xl++;
					gotoxy(hout, xl, yl);
				}
			}
		}
	}
	else if (x == '2')
	{
		while (1)
		{
			m = _getch();
			if (m == ' ')
			{
				showch(hout, xl, yl, ' ');
				gotoxy(hout, xl, yl);
			}
			if (m == 'Q' || m == 'q')
				break;
			if (m == 'I' || m == 'i')
			{
				if (yl == 1)
				{
					yl = 17;
					gotoxy(hout, xl, yl);
				}
				else
				{
					yl--;
					gotoxy(hout, xl, yl);
				}
			}
			if (m == 'K' || m == 'k')
			{
				if (yl == 17)
				{
					yl = 1;
					gotoxy(hout, xl, yl);
				}
				else
				{
					yl++;
					gotoxy(hout, xl, yl);
				}
			}
			if (m == 'J' || m == 'j')
			{
				if (xl == 1)
				{
					xl = 69;
					gotoxy(hout, xl, yl);
				}
				else
				{
					xl--;
					gotoxy(hout, xl, yl);
				}
			}
			if (m == 'L' || m == 'l')
			{
				if (xl == 69)
				{
					xl = 1;
					gotoxy(hout, xl, yl);
				}
				else
				{
					xl++;
					gotoxy(hout, xl, yl);
				}
			}
		}
	}
	else if (x == '5')
	{
		while (1)
		{
			m = _getch();
			if (m == 224)
			{
				_getch();
				continue;
			}
			if (m == ' ')
			{
				showch(hout, xl, yl, ' ');
				gotoxy(hout, xl, yl);
			}
			if (m == 'Q' || m == 'q')
				break;
			if (m == 'I' || m == 'i')
			{
				if (yl == 1)
					continue;
				else
				{
					yl--;
					gotoxy(hout, xl, yl);
				}
			}
			if (m == 'K' || m == 'k')
			{
				if (yl == 17)
					continue;
				else
				{
					yl++;
					gotoxy(hout, xl, yl);
				}
			}
			if (m == 'J' || m == 'j')
			{
				if (xl == 1)
					continue;
				else
				{
					xl--;
					gotoxy(hout, xl, yl);
				}
			}
			if (m == 'L' || m == 'l')
			{
				if (xl == 69)
					continue;
				else
				{
					xl++;
					gotoxy(hout, xl, yl);
				}
			}
		}
	}
	else if (x == '6')
	{
		while (1)
		{
			m = _getch();
			if (m == 224)
			{
				_getch();
				continue;
			}
			if (m == ' ')
			{
				showch(hout, xl, yl, ' ');
				gotoxy(hout, xl, yl);
			}
			if (m == 'Q' || m == 'q')
				break;
			if (m == 'I' || m == 'i')
			{
				if (yl == 1)
				{
					yl = 17;
					gotoxy(hout, xl, yl);
				}
				else
				{
					yl--;
					gotoxy(hout, xl, yl);
				}
			}
			if (m == 'K' || m == 'k')
			{
				if (yl == 17)
				{
					yl = 1;
					gotoxy(hout, xl, yl);
				}
				else
				{
					yl++;
					gotoxy(hout, xl, yl);
				}
			}
			if (m == 'J' || m == 'j')
			{
				if (xl == 1)
				{
					xl = 69;
					gotoxy(hout, xl, yl);
				}
				else
				{
					xl--;
					gotoxy(hout, xl, yl);
				}
			}
			if (m == 'L' || m == 'l')
			{
				if (xl == 69)
				{
					xl = 1;
					gotoxy(hout, xl, yl);
				}
				else
				{
					xl++;
					gotoxy(hout, xl, yl);
				}
			}
		}
	}
}

void move_by_arrow(const HANDLE hout, int x)
{
	int m, xa, ya;
	int a1 = 0;
	int a2 = 0;
	xa = (MAX_X + 1) / 2;
	ya = (MAX_Y + 1) / 2;

	if (x == '3')
	{
		while (1)
		{
			m = _getch();
			if (m == ' ')
			{
				showch(hout, xa, ya, ' ');
				gotoxy(hout, xa, ya);
			}
			if (m == 'q' || m == 'Q')
				break;
			if (m == 224)
			{
				m = _getch();

				if (m == 72)
				{
					if (ya == 1)
						continue;
					else
					{
						ya--;
						gotoxy(hout, xa, ya);
					}
				}
				if (m == 75)
				{
					if (xa == 1)
						continue;
					else
					{
						xa--;
						gotoxy(hout, xa, ya);
					}
				}
				if (m == 80)
				{
					if (ya == 17)
						continue;
					else
					{
						ya++;
						gotoxy(hout, xa, ya);
					}
				}
				if (m == 77)
				{
					if (xa == 69)
						continue;
					else
					{
						xa++;
						gotoxy(hout, xa, ya);
					}
				}
			}
		}
	}
	else if (x == '4')
	{
		while (1)
		{
			m = _getch();
			if (m == ' ')
			{
				showch(hout, xa, ya, ' ');
				gotoxy(hout, xa, ya);
			}
			if (m == 'q' || m == 'Q')
				break;
			if (m == 224)
			{
				m = _getch();

				if (m == 72)
				{
					if (ya == 1)
					{
						ya = 17;
						gotoxy(hout, xa, ya);
					}
					else
					{
						ya--;
						gotoxy(hout, xa, ya);
					}
				}
				if (m == 75)
				{
					if (xa == 1)
					{
						xa = 69;
						gotoxy(hout, xa, ya);
					}
					else
					{
						xa--;
						gotoxy(hout, xa, ya);
					}
				}
				if (m == 80)
				{
					if (ya == 17)
					{
						ya = 1;
						gotoxy(hout, xa, ya);
					}
					else
					{
						ya++;
						gotoxy(hout, xa, ya);
					}
				}
				if (m == 77)
				{
					if (xa == 69)
					{
						xa = 1;
						gotoxy(hout, xa, ya);
					}
					else
					{
						xa++;
						gotoxy(hout, xa, ya);
					}
				}
			}
		}
	}
}

/***************************************************************************
  函数名称：
  功    能：
  输入参数：
  返 回 值：
  说    明：main函数仅用于初始演示，可以按题目要求全部推翻重写
***************************************************************************/
int main()
{
	while (1) {
		int x, y;
		int c_in;
		const HANDLE hout = GetStdHandle(STD_OUTPUT_HANDLE); //取标准输出设备对应的句柄
		x = (MAX_X + 1) / 2;
		y = (MAX_Y + 1) / 2;

		/* 生成伪随机数的种子，只需在程序开始时执行一次即可 */
		srand((unsigned int)(time(0)));


		/* 此句的作用是调用系统的cls命令清屏 */
		cls(hout);
		c_in = menu(hout);
		if (c_in == '0') {
			break;
		}
		else {
			/* 显示初始的边框及其中的随机字符 */
			init_border(hout);
			gotoxy(hout, x, y);

			if (c_in == '1' || c_in == '2' || c_in == '5' || c_in == '6') {
				move_by_ijkl(hout, c_in);
			}
			else {
				move_by_arrow(hout, c_in);
			}

			gotoxy(hout, 0, 23);
			cout << "游戏结束，按回车键返回菜单.";
			while (1) {
				if (_getch() == 13)
					break;
			}
		}
	}
	return 0;

}