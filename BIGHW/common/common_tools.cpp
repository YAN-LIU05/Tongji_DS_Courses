/* 2352018 大数据 刘彦 */
#include <iostream>
#include <cstdlib> 
#include <ctime> 
#include <windows.h>
#include <conio.h>
#include <iomanip>
#include "../include/bighw.h"
#include "../include/cmd_console_tools.h"

using namespace std;

/***************************************************************************
  函数名称：
  功    能：求字符串str的长度
  输入参数：
  返 回 值：字符串长度
  说    明：
***************************************************************************/
int tj_strlen(const char* str)
{
	/* 注意：函数内不允许定义任何形式的数组（包括静态数组） */
	int length = 0;
	if (str == NULL)
	{
		return 0;
	}

	while (*str != '\0')
	{
		length++;
		str++;
	}

	return length;
}

/***************************************************************************
  函数名称：
  功    能：将字符串s2复制到s1中,覆盖s1中原内容,复制时包含\0
  输入参数：
  返 回 值：新的s1
  说    明：
***************************************************************************/
char* tj_strcpy(char* s1, const char* s2)
{
	/* 注意：函数内不允许定义任何形式的数组（包括静态数组） */
	if (s1 == NULL)
	{
		return s1;
	}

	char* s = s1;

	if (s2 == NULL)
	{
		*s = '\0';
	}
	else
	{
		for (; *s2 != '\0'; s++, s2++)
		{
			*s = *s2;
		}
		*s = '\0';
	}

	return s1;
}

/***************************************************************************
  函数名称：
  功    能：比较字符串s1和s2的大小,英文字母不分大小写
  输入参数：
  返 回 值：相等为0,不等则为第1个不相等字符的ASCII差值
  说    明：
***************************************************************************/
int tj_strcasecmp(const char* s1, const char* s2)
{
	/* 注意：函数内不允许定义任何形式的数组（包括静态数组） */
	if (s1 == NULL || s2 == NULL)
	{
		int t = (s1 != NULL) - (s2 != NULL);
		return t;
	}
	char s_1, s_2;
	while (1)
	{
		if (*s1 >= 'A' && *s1 <= 'Z')
		{
			s_1 = *s1 + 'a' - 'A';
		}
		else
		{
			s_1 = *s1;
		}
		if (*s2 >= 'A' && *s2 <= 'Z')
		{
			s_2 = *s2 + 'a' - 'A';
		}
		else
		{
			s_2 = *s2;
		}
		if (s_1 == s_2)
		{
			if (s_1 == '\0')
				break;
			s1++;
			s2++;
		}
		else
		{
			break;
		}
	}
	return s_1 - s_2;
}

/***************************************************************************
  函数名称：print_origin
  功    能：打印初始数组
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void print_origin(int rows, int cols, int array[][MAX_ROWS], int num1, int num2)
{

	cout << "  | ";
	if (num2 == 0)
	{
		for (int j = 0; j < cols; ++j)
			cout << " " << j + 1 << " ";
	}
	else if (num2 == 1)
	{
		for (int j = 0; j < cols; ++j)
			cout << " " << j << " ";
	}
	cout << endl;
	cout << "--+-";;
	for (int i = 0; i < cols; ++i)
		cout << "---";
	cout << endl;
	for (int i = 0; i < rows; ++i)
	{
		cout << static_cast<char>('A' + i) << " | ";
		if (num1 == 1)
		{
			for (int j = 0; j < cols; ++j)
				cout << " " << array[i][j] << " ";
		}
		else if (num1 == 0)
		{
			for (int j = 0; j < cols; ++j)
			{
				if (array[i][j] == 1)
				{
					cout << " " << "*" << " ";

				}
				else
				{
					cout << " " << "0" << " ";
				}
			}

		}
		cout << endl;
	}
	cout << endl;
}

/***************************************************************************
  函数名称：zero_drop
  功    能：非零元素下移
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void zero_drop(int array[MAX_ROWS][MAX_COLS], int rows, int cols)
{
	// 从矩阵底部开始向上遍历，让0上面的非0元素下移
	for (int j = 0; j < cols; ++j)   //从矩阵底部开始向上遍历
	{
		for (int i = rows - 1; i >= 0; --i)   //如果当前元素是0，则需要下移上面的非0元素
		{
			if (array[i][j] == 0)  //从当前位置向上查找第一个非0元素
			{
				for (int k = i - 1; k >= 0; --k)
				{
					if (array[k][j] != 0)
					{
						// 将找到的非0元素移动到当前0的位置
						array[i][j] = array[k][j];
						// 并将原来的位置设置为0
						array[k][j] = 0;
						break;
					}
				}
			}
		}
	}
}

/***************************************************************************
  函数名称：draw_border
  功    能：画出边框
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void draw_border(int rows, int cols, bool border, int choice, int which)
{
	if (which == 1)
	{
		cout << endl;
		cct_gotoxy(0, 1);
		int temp = rows;
		rows = cols;
		cols = temp;
		cct_gotoxy(0, 1);
		int hight = (border) ? cols * 3 + (cols - 1) : cols * 3;
		set_botton(true, border ? hight + 3 : hight + 2);

		cct_setcolor(COLOR_HWHITE, COLOR_BLACK);
		if (!border)
		{
			cct_setcolor(COLOR_HWHITE, COLOR_BLACK);
			cout << "╔ "; 
			for (int i = 0; i < rows; i++) 
			{
				cout << "═ ";
				if (choice == 4)
					Sleep(TIME);
			}
			cout << "╗ ";
			for (int i = 0; i < cols; i++)
			{
				cct_gotoxy(0, i + 2);
				cout << "║ ";
				cct_gotoxy(rows * 2 + 2, i + 2);
				cout << "║ ";
				if (choice == 4)
					Sleep(TIME);
			}
			cct_gotoxy(0, cols + 2);
			cout << "╚ ";
			for (int i = 0; i < rows; i++) 
			{
				cout << "═ ";
				if (choice == 4)
					Sleep(TIME);
			}
			cout << "╝ ";
		}

		if (border)
		{
			cct_setcolor(COLOR_HWHITE, COLOR_BLACK);
			cout << "╔ ";
			for (int i = 0; i < rows; i++)
			{
				cout << "═ ";
				if (choice == 5)
					Sleep(TIME);
				if (i == rows - 1)
					break;
				cout << "╦ ";
				if (choice == 5)
					Sleep(TIME);
			}

			cout << "╗ ";
			for (int i = 0; i < cols * 2; i += 2)
			{
				for (int j = 0; j <= rows * 4; j += 4)
				{

					if (j == 0)
					{
						cct_gotoxy(0, i + 2);
						cout << "║  ";
					}
					if (j == rows * 4)
					{
						cct_gotoxy(j - 1, i + 2);
						cout << " ║ ";
					}
					if (j > 0 && j < rows * 4)
					{
						cct_gotoxy(j - 1, i + 2);
						cout << " ║  ";
					}

					if (choice == 5)
						Sleep(TIME);
				}
				if (i < cols * 2 - 2)
				{
					cct_gotoxy(0, i + 3);
					cout << "╠ ";
					for (int i = 0; i < rows; i++)
					{
						cout << "═ ";
						if (choice == 5)
							Sleep(TIME);
						if (i == rows - 1)
							break;
						cout << "╬ ";
						if (choice == 5)
							Sleep(TIME);
					}
					cout << "╣ ";
				}
			}
			cct_gotoxy(0, cols * 2 + 1);
			cout << "╚ ";
			for (int i = 0; i < rows; i++)
			{
				cout << "═ ";
				if (choice == 5)
					Sleep(TIME);
				if (i == rows - 1)
					break;
				cout << "╩ ";
				if (choice == 5)
					Sleep(TIME);
			}
			cout << "╝ ";
		}
	}



	if (which == 2)
	{
		cout << endl;
		//第一行标头
		cout << " ";
		Sleep(5);
		for (int i = 0; i < cols; i++)
		{
			if (i == 0)
				cout << setw(6) << i;
			else
				cout << setw(6 + border * 2) << i;
		}
		cout << endl;

		//第一行外框线
		cout << "  ";
		Sleep(5);
		cct_setcolor(COLOR_HWHITE, COLOR_BLACK);
		cout << "╔ ";
		Sleep(5);
		for (int i = 0; i < cols; i++)
		{
			cout << "═ ═ ═ ";
			if ((border == 1) && (i != cols - 1))
				cout << "╦ ";
			Sleep(5);
		}
		cout << "╗ ";
		Sleep(5);
		cct_setcolor(COLOR_BLACK, COLOR_WHITE);
		cout << endl;

		//中部
		for (int i = 0; i < rows; i++)
		{
			cout << "  ";
			Sleep(5);
			single_outline(cols, border);
			cout << endl;
			cout << (char)('A' + i) << " ";
			Sleep(5);
			single_outline(cols, border);
			cout << endl;
			cout << "  ";
			Sleep(5);
			single_outline(cols, border);
			cout << endl;
			if ((i != rows - 1) && (border == 1))
			{
				cout << "  ";
				Sleep(5);
				cct_setcolor(COLOR_HWHITE, COLOR_BLACK);
				cout << "╠ ";
				Sleep(5);
				for (int i = 0; i < cols; i++)
				{
					cout << "═ ═ ═ ";
					if (i != cols - 1)
					{
						cout << "╬ ";
					}
					Sleep(5);
				}
				cout << "╣ ";
				Sleep(5);
				cct_setcolor(COLOR_BLACK, COLOR_WHITE);
				cout << endl;
			}
		}

		//最后一行外框线
		cout << "  ";
		Sleep(5);
		cct_setcolor(COLOR_HWHITE, COLOR_BLACK);
		cout << "╚ ";
		Sleep(5);
		for (int i = 0; i < cols; i++)
		{
			cout << "═ ═ ═ ";
			if ((border == 1) && (i != cols - 1))
				cout << "╩ ";
			Sleep(5);
		}
		cout << "╝ ";
		Sleep(5);
	}
	cct_setcolor(COLOR_BLACK, COLOR_WHITE);
	cout << endl;

}

/***************************************************************************
  函数名称：set_botton
  功    能：设置坐标
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void set_botton(bool set, int num)
{
	static int Y = 0;
	if (set)
		Y = num;
	else
		cct_gotoxy(0, Y);
}

/***************************************************************************
	函数名称：element_fall
	功    能  二维数组的下落操作
	输入参数：
	返 回 值：
	说    明：
***************************************************************************/
void element_fall(int array[][MAX_COLS], int array_around[][MAX_COLS], int rows, int cols, int have_block, int border) {
	// 将色块位置置为 0
	for (int j = 0; j < cols; j++) {
		for (int i = 0; i < rows; i++) {
			if (array_around[i][j] == '*') {
				array[i][j] = 0; // 直接操作
			}
		}
	}

	// 冒泡操作，将 0 冒泡到下方
	int is_stable;
	do {
		is_stable = 1; // 假设当前状态稳定
		for (int j = 0; j < cols; j++) {
			for (int i = rows - 1; i > 0; i--) {
				if (array[i][j] == 0 && array[i - 1][j] != 0) {
					// 交换
					int temp = array[i - 1][j];
					array[i - 1][j] = array[i][j];
					array[i][j] = temp;

					// 如果有色块操作，进行颜色处理
					if (have_block == 1) {
						draw_block(i, j, border, array, rows, cols, 1);
						Sleep(5);
						draw_block(i - 1, j, border, array, rows, cols, 0);
					}
					is_stable = 0; // 标记为不稳定
				}
			}
		}
	} while (!is_stable); // 直到状态稳定为止
}

/***************************************************************************
	函数名称：draw_block
	功    能：画一个色块
	输入参数：
	返 回 值：
	说    明：以X,Y为中心画色块，即X,Y为星星位置
***************************************************************************/
void draw_block(int i, int j, int border, int array[][MAX_COLS], int rows, int cols, int state)
{
	int X, Y;
	int color_fg = 0, color_bg = 0;

	//对0不进行显示操作
	if (array[i][j] == 0)
		state = 0;
	switch (state)
	{
		case 1:
			color_fg = COLOR_BLACK;
			color_bg = array[i][j] + 8;
			break;
		case -1:
			color_fg = COLOR_HWHITE;
			color_bg = array[i][j] + 8;
			break;
		case -2:
			color_fg = COLOR_WHITE;
			color_bg = array[i][j] + 8;
			break;
		case 0: // 消除了的星星
			color_fg = COLOR_HWHITE;
			color_bg = COLOR_HWHITE;
			break;
	}

	cct_setcolor(color_bg, color_fg);
	location_trans(1, i, j, X, Y, rows, cols, border);
	cct_gotoxy(X - 2, Y - 1);
	cout << "╔ ═ ╗ ";
	cct_gotoxy(X - 2, Y);
	cout << "║ ★║ ";
	cct_gotoxy(X - 2, Y + 1);
	cout << "╚ ═ ╝ ";
	cct_setcolor(COLOR_BLACK, COLOR_WHITE);
}

/***************************************************************************
	函数名称：location_trans
	功    能：做一个array内部数组行列与伪图形中心星星坐标位置转换的函数
	输入参数：
	返 回 值：
	说    明：1 从数组行列求伪界面横纵坐标 反之为-1
***************************************************************************/
void location_trans(const int drc, int& i, int& j, int& X, int& Y, int rows, int cols, int border)
{
	// 计算 Y 和 X 的位置
	if (drc == 1)
	{
		Y = 4 + (3 + border) * i;
		X = 6 + (6 + border * 2) * j;
	}
	else if (drc == -1)
	{
		// 在合法区域内的范围
		int y_min = 3;
		int y_max = (border == 0) ? 3 + rows * 3 : 3 + rows * (3 + border);
		int x_min = 4;
		int x_max = 4 + (6 + border * 2) * cols;

		if ((Y >= y_min && Y < y_max) && (X >= x_min && X < x_max))
		{
			if (border == 1)
			{
				if (((Y - 3) % 4 >= 0 && (Y - 3) % 4 <= 2) && ((X - 4) % 8 >= 0 && (X - 4) % 8 <= 5))
				{
					i = (Y - 3) / (3 + border);
					j = (X - 4) / (6 + border * 2);
				}
				else
				{
					i = -1;
					j = -1;
				}
			}
			else
			{
				i = (Y - 3) / (3 + border);
				j = (X - 4) / (6 + border * 2);
			}
		}
		else
		{
			i = -1;
			j = -1;
		}
	}
}

/***************************************************************************
	函数名称：single_outline
	功    能：其中一行的初始外框线
	输入参数：
	返 回 值：
	说    明：
***************************************************************************/
void single_outline(int col, const int border)
{
	cct_setcolor(COLOR_HWHITE, COLOR_BLACK);
	cout << "║ ";
	Sleep(5);
	for (int i = 0; i < col; i++)
	{
		int x, y;
		cct_getxy(x, y);
		cct_showch(x, y, ' ', COLOR_HWHITE, COLOR_BLACK, 6);
		if ((i != col - 1) && (border == 1))
		{
			cout << "║ ";
			Sleep(5);
		}
		Sleep(5);
	}
	cout << "║ ";
	Sleep(5);
	cct_setcolor(COLOR_BLACK, COLOR_WHITE);
}

/***************************************************************************
	函数名称：find_empty_above
	功    能：在指定列上查找从当前行向上直到第一行的第一个非零元素
	输入参数：
	返 回 值：
	说    明：
***************************************************************************/
int find_empty_above(int i_last, int j_last, int array[][MAX_COLS], int rows)
{
	for (int i = rows - 1; i >= 0; i--)
	{
		if (array[i][j_last] != 0)
		{
			return i + 1;
		}
	}
	return 0; // 如果没有找到，返回0
}

/***************************************************************************
	函数名称：fill_array
	功    能：填充数组
	输入参数：
	返 回 值：
	说    明：
***************************************************************************/
void fill_array(int array[MAX_ROWS][MAX_COLS], int rows, int cols, int num)
{
	int opt = 0;
	switch (num)
	{
		case 1:
			opt = 9;
			break;
		case 2:
			opt = 5;
			break;
	}
	srand(static_cast<unsigned int>(time(nullptr)));
	for (int i = 0; i < rows; ++i) 
	{
		for (int j = 0; j < cols; ++j) 
		{
			array[i][j] = (rand() % opt) + 1; // 填充1到9之间的随机数
		}
	}
}

/***************************************************************************
	函数名称：copy_array
	功    能：复制数组
	输入参数：
	返 回 值：
	说    明：
***************************************************************************/
void copy_array(const int source[MAX_ROWS][MAX_COLS], int destination[MAX_ROWS][MAX_COLS], int rows, int cols) 
{
	for (int i = 0; i < rows; ++i) 
	{
		for (int j = 0; j < cols; ++j) 
		{
			destination[i][j] = source[i][j];
		}
	}
}

/***************************************************************************
  函数名称：base_check0
  功    能：检查是否可以消除
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
bool base_check0(const int array[MAX_ROWS][MAX_COLS], int row, int col, int rows, int cols)
{
	if (row >= rows || col >= cols)
		return 0;

	int count = 1; // 从目标元素开始计数
	for (int j = col + 1; j < cols && count < 3; j++) //向右检查
	{
		if (array[row][j] == array[row][col])
		{
			count++;
			if (count >= 3)
				return 1;
		}
		else
			break; // 遇到不同的元素，停止检查
	}
	for (int j = col - 1; j >= 0 && count < 3; j--) //向左检查
	{
		if (array[row][j] == array[row][col])
		{
			count++;
			if (count >= 3)
				return 1;
		}
		else
			break; // 遇到不同的元素，停止检查
	}

	count = 1; // 重置计数
	for (int i = row + 1; i < rows && count < 3; i++) //向下检查
	{
		if (array[i][col] == array[row][col])
		{
			count++;
			if (count >= 3)
				return 1;
		}
		else
			break; // 遇到不同的元素，停止检查
	}
	for (int i = row - 1; i >= 0 && count < 3; i--) //向上检查
	{
		if (array[i][col] == array[row][col])
		{
			count++;
			if (count >= 3)
				return 1;
		}
		else
			break; // 遇到不同的元素，停止检查
	}

	return 0; // 没有找到可消除项
}

/***************************************************************************
  函数名称：base_check1
  功    能：检查是否有初始可消除项
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
bool base_check1(const int array[MAX_ROWS][MAX_COLS], int rows, int cols)
{
	int num = 0;
	for (int i = 0; i < rows; ++i)
	{
		for (int j = 0; j < cols; ++j)
		{
			if (base_check0(array, i, j, rows, cols))
				num++;
		}
	}
	if (num)
		return 1;
	else
		return 0;
}

/***************************************************************************
  函数名称：base_check2
  功    能：检查是否可以提示
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
bool base_check2(const int array[MAX_ROWS][MAX_COLS], const int directions[4][2], int row, int col, int rows, int cols)
{
	if (row < 0 || row >= rows || col < 0 || col >= cols)
		return 0;

	// 创建一个数组的副本以模拟交换
	int arrayCopy[MAX_ROWS][MAX_COLS];
	copy_array(array, arrayCopy, rows, cols);

	// 检查相邻元素交换后是否满足消除条件
	for (int i = 0; i < 4; ++i)
	{
		int nextRow = row + directions[i][0];
		int nextCol = col + directions[i][1];
		if (nextRow >= 0 && nextRow < rows && nextCol >= 0 && nextCol < cols)   //交换
		{
			int temp = arrayCopy[nextRow][nextCol];
			arrayCopy[nextRow][nextCol] = arrayCopy[row][col];
			arrayCopy[row][col] = temp;

			if (col - 1 >= 0 && row - 1 >= 0)
			{
				if (base_check0(arrayCopy, row, col, rows, cols) || base_check0(arrayCopy, row + 1, col, rows, cols) || base_check0(arrayCopy, row - 1, col, rows, cols)
					|| base_check0(arrayCopy, row, col + 1, rows, cols) || base_check0(arrayCopy, row, col - 1, rows, cols))
					return 1;
			}
			else if (col - 1 >= 0 && row - 1 < 0)
			{
				if (base_check0(arrayCopy, row, col, rows, cols) || base_check0(arrayCopy, row + 1, col, rows, cols) || base_check0(arrayCopy, row, col + 1, rows, cols)
					|| base_check0(arrayCopy, row, col - 1, rows, cols))
					return 1;
			}
			else if (col - 1 < 0 && row - 1 >= 0)
			{
				if (base_check0(arrayCopy, row, col, rows, cols) || base_check0(arrayCopy, row + 1, col, rows, cols) || base_check0(arrayCopy, row - 1, col, rows, cols)
					|| base_check0(arrayCopy, row, col + 1, rows, cols))
					return 1;
			}
			else
			{
				if (base_check0(arrayCopy, row, col, rows, cols) || base_check0(arrayCopy, row + 1, col, rows, cols) || base_check0(arrayCopy, row, col + 1, rows, cols))
					return 1;
			}

			// 恢复交换前的数组状态
			temp = arrayCopy[nextRow][nextCol];
			arrayCopy[nextRow][nextCol] = arrayCopy[row][col];
			arrayCopy[row][col] = temp;
		}
	}

	return 0;
}
