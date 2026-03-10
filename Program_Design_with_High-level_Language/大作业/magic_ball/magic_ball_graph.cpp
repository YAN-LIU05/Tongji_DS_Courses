/* 2352018 信06 刘彦 */
#include <iostream>
#include <conio.h>
#include <iomanip>
#include <windows.h>
#include "cmd_console_tools.h"
#include "magic_ball.h"

using namespace std;

/***************************************************************************
  函数名称：draw_ball
  功    能：画出彩球
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void draw_ball(int i, int j, int color, int border)
{
	int x, y;
	if (!border)
	{
		x = 2 * j + 2;
		y = i + 2;
		cct_gotoxy(x, y);
		cct_setcolor(color, COLOR_BLACK);
		cout << "〇";
		cct_gotoxy(x, y + 1);
	}
	if (border == 1)
	{
		x = 4 * j + 2;
		y = 2 * i + 2;
		cct_gotoxy(x, y);
		if (color == COLOR_HWHITE)
			cct_setcolor(color, COLOR_HWHITE);
		else
			cct_setcolor(color, COLOR_BLACK);
		cout << "〇";
		cct_gotoxy(x, y + 1);

	}
	if (border == 2)
	{
		x = 4 * j + 2;
		y = 2 * i + 2;
		cct_gotoxy(x, y);
		if (color == COLOR_HWHITE)
			cct_setcolor(color, COLOR_HWHITE);
		else
		{
			cct_setcolor(color, COLOR_BLACK);
		}
		cout << "◎";
		cct_gotoxy(x, y + 1);


	}
}

/***************************************************************************
  函数名称：draw_border
  功    能：画出边框
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void draw_border(int row, int column, bool border, int choice)
{

	cout << endl;
	cct_gotoxy(0, 1);
	int temp = row;
	row = column;
	column = temp;
	cct_gotoxy(0, 1);
	int hight = (border) ? column * 3 + (column - 1) : column * 3;
	set_botton(true, border ? hight + 3 : hight + 2);

	cct_setcolor(COLOR_HWHITE, COLOR_BLACK);
	if (!border)
	{
		cct_setcolor(COLOR_HWHITE, COLOR_BLACK);
		cout << "╔";
		for (int i = 0; i < row; i++) {
			cout << "═";
			if (choice == 4)
				Sleep(TIME);
		}
		cout << "╗";
		for (int i = 0; i < column; i++)
		{
			cct_gotoxy(0, i + 2);
			cout << "║";
			cct_gotoxy(row * 2 + 2, i + 2);
			cout << "║";
			if (choice == 4)
				Sleep(TIME);
		}
		cct_gotoxy(0, column + 2);
		cout << "╚";
		for (int i = 0; i < row; i++) {
			cout << "═";
			if (choice == 4)
				Sleep(TIME);
		}
		cout << "╝";
	}

	if (border)
	{
		cct_setcolor(COLOR_HWHITE, COLOR_BLACK);
		cout << "╔";
		for (int i = 0; i < row; i++)
		{
			cout << "═";
			if (choice == 5)
				Sleep(TIME);
			if (i == row - 1)
				break;
			cout << "╦";
			if (choice == 5)
				Sleep(TIME);
		}

		cout << "╗";
		for (int i = 0; i < column * 2; i += 2)
		{
			for (int j = 0; j <= row * 4; j += 4)
			{

				if (j == 0)
				{
					cct_gotoxy(0, i + 2);
					cout << "║ ";
				}
				if (j == row * 4)
				{
					cct_gotoxy(j - 1, i + 2);
					cout << " ║";
				}
				if (j > 0 && j < row * 4)
				{
					cct_gotoxy(j - 1, i + 2);
					cout << " ║ ";
				}

				if (choice == 5)
					Sleep(TIME);
			}
			if (i < column * 2 - 2)
			{
				cct_gotoxy(0, i + 3);
				cout << "╠";
				for (int i = 0; i < row; i++)
				{
					cout << "═";
					if (choice == 5)
						Sleep(TIME);
					if (i == row - 1)
						break;
					cout << "╬";
					if (choice == 5)
						Sleep(TIME);
				}
				cout << "╣";
			}
		}
		cct_gotoxy(0, column * 2 + 1);
		cout << "╚";
		for (int i = 0; i < row; i++)
		{
			cout << "═";
			if (choice == 5)
				Sleep(TIME);
			if (i == row - 1)
				break;
			cout << "╩";
			if (choice == 5)
				Sleep(TIME);
		}
		cout << "╝";
	}
	cct_setcolor(COLOR_BLACK, COLOR_WHITE);
	cout << endl;
}

/***************************************************************************
  函数名称：draw_fall
  功    能：除零并画出下落
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
int draw_fall(int array[MAX_ROWS][MAX_COLS], int rows, int cols, int choice, int array0[MAX_ROWS][MAX_COLS], int have_score)
{
	int x, y;
	int x0, y0;
	int score = 0;
	cout << endl;
	cct_setcolor(COLOR_BLACK, COLOR_WHITE);// 重置颜色
	cct_getxy(x0, y0);

	if (choice == 7)
	{
		cout << "按回车键进行数组下落除0操作...";
		char ch1 = _getch();
		while (1)
		{
			if (ch1 == '\r')
				break;
			ch1 = _getch();

		}
	}

	for (int i = 0; i < rows; i++)
	{
		for (int j = 0; j < cols; j++)
		{
			x = 4 * j + 2;
			y = 2 * i + 2;
			cct_gotoxy(x, y);
			if (base_check0(array0, i, j, rows, cols))
			{
				cct_setcursor(CURSOR_INVISIBLE);
				for (int k = 0; k < 5; k++) {
					draw_ball(i, j, array[i][j], 1);
					Sleep(TIME * 2);
					draw_clean(i, j, array[i][j]);
					Sleep(TIME * 2);
				}
				draw_clean(i, j, COLOR_HWHITE);

			}
			cct_gotoxy(x, y + 1);
		}
	}

	bool can_remove = 1;
	do {

		can_remove = 0;
		// 记录可消除项的位置和数量
		int remove_position[100][2];
		int remove_count = 0;

		// 寻找可消除项并记录位置
		for (int i = 0; i < rows; ++i)
		{
			for (int j = 0; j < cols; ++j)
			{
				if (base_check0(array0, i, j, rows, cols))
				{
					remove_position[remove_count][0] = i; // 行
					remove_position[remove_count][1] = j; // 列
					remove_count++;
					can_remove = 1;
				}
			}
		}

		if (!can_remove)
			break;

		// 执行消除操作：将可消除项设置为0
		for (int k = 0; k < remove_count; ++k)
		{
			int i = remove_position[k][0];
			int j = remove_position[k][1];
			array0[i][j] = 0;
		}

		if (have_score == 1)
		{
			for (int i = 0; i < rows; ++i)
			{
				for (int j = 0; j < cols; ++j)
				{
					if (array0[i][j] == 0)
						score++;
				}
			}
		}


		//从矩阵底部开始向上遍历，让0上面的非0元素下移
		for (int j = 0; j < cols; ++j)   //从矩阵底部开始向上遍历
		{
			for (int i = rows - 1; i >= 0; --i)   //如果当前元素是0，则需要下移上面的非0元素
			{
				if (array0[i][j] == 0)  //从当前位置向上查找第一个非0元素
				{
					for (int k = i - 1; k >= 0; --k)
					{
						if (array0[k][j] != 0)
						{

							// 将找到的非0元素移动到当前0的位置
							cct_showstr(2 + 4 * j, 2 + 2 * k, "  ", COLOR_HWHITE, 0, 1);
							draw_ball(i, j, array0[k][j], 1);
							array0[i][j] = array0[k][j];
							Sleep(TIME * 5);
							// 并将原来的位置设置为0
							array0[k][j] = 0;
							break;
						}
					}
				}
				Sleep(TIME);
			}
			Sleep(TIME);
		}


		if (choice == 7)
		{
			cct_setcolor(COLOR_BLACK, COLOR_WHITE);// 重置颜色
			cct_gotoxy(x0, y0);
			cout << "                              ";
			cct_gotoxy(x0, y0);
			cout << "按回车键进行新值填充...";
			char ch2 = _getch();
			while (1)
			{
				if (ch2 == '\r')
					break;
				ch2 = _getch();

			}
		}

		srand(static_cast<unsigned int>(time(nullptr)));

		for (int i = 0; i < rows; ++i) {
			for (int j = 0; j < cols; ++j) {
				// 检查并标记可消除项
				if (array0[i][j] == 0) {

					array0[i][j] = (rand() % 9) + 1;
					draw_ball(i, j, array0[i][j], 1);
					Sleep(TIME * 5);
				}
			}
		}

		cct_setcolor(COLOR_BLACK, COLOR_WHITE);// 重置颜色
		cct_gotoxy(x0, y0);
		break;
		cout << "                                          ";
		cct_gotoxy(x0, y0);

	} while (can_remove); // 如果有可消除项，重复以上过程	


	if (choice == 7)
	{

		cout << "按回车键显示消除提示...";
		char ch3 = _getch();
		while (1)
		{
			if (ch3 == '\r')
				break;
			ch3 = _getch();
		}
	}

	int directions[4][2] = { {-1, 0}, {1, 0}, {0, -1}, {0, 1} };   //方向数组

	for (int i = 0; i < rows; ++i)
	{
		for (int j = 0; j < cols; ++j)
		{
			// 检查并标记可消除项
			if (base_check2(array0, directions, i, j, rows, cols))
			{
				draw_ball(i, j, array0[i][j], 2);
			}

		}
	}
	cct_setcolor(COLOR_BLACK, COLOR_WHITE);// 重置颜色
	cct_gotoxy(x0, y0);
	return score;
}

/***************************************************************************
  函数名称：draw_clean
  功    能：消除彩球
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void draw_clean(int i, int j, int color)
{
	int x, y;
	x = 4 * j + 2;
	y = 2 * i + 2;
	cct_gotoxy(x, y);
	cct_setcolor(color, color);
	cout << "  ";
	cct_gotoxy(x, y + 1);
}

/***************************************************************************
  函数名称：draw_nine
  功    能：第9步的汇总函数
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void draw_nine(int array[MIN_ROWS][MAX_ROWS], int rows, int cols, int choice)
{
	int a, b, c, d;
	int x, y;
	int x9, y9;
	int X = 0, Y = 0;   //鼠标位置
	int ret, maction;
	int keycode1, keycode2;
	int loop = 1;
	char hang;
	int lie;
	int directions[4][2] = { {-1, 0}, {1, 0}, {0, -1}, {0, 1} };   //方向数组
	int score = 0, score0 = 0;
	int arrayCopy0[MAX_ROWS][MAX_COLS];
	x9 = 0;
	y9 = 2 * rows + 2;
	for (int i = 0; i < rows; ++i)
	{
		for (int j = 0; j < cols; ++j)
			arrayCopy0[i][j] = array[i][j];
	}
	cct_cls();
	cct_getconsoleborder(a, b, c, d);
	cct_setcolor();
	cct_cls();
	d = 2 * cols + 5;
	c = rows * 4 + 4;
	cct_setconsoleborder(c + 25, d + 4);
	cct_gotoxy(0, 0);
	cct_setfontsize("新宋体", 28);
	cout << "屏幕：" << d << "行" << 40 << "列";
	cout << "(当前分数：" << score << ")";
	int arrayCopy[MAX_ROWS][MAX_COLS];

	draw_border(rows, cols, 1, choice);
	int count = 0;
	if (count == 0)
	{
		for (int i = 0; i < rows; ++i)
		{
			for (int j = 0; j < cols; ++j)
				arrayCopy[i][j] = arrayCopy0[i][j];
		}
	}



	if (base_check1(arrayCopy0, rows, cols))
	{
		for (int i = 0; i < rows; i++)
		{
			for (int j = 0; j < cols; j++)
			{
				x = 4 * j + 2;
				y = 2 * i + 2;
				cct_gotoxy(x, y);
				cct_setcolor(arrayCopy0[i][j], COLOR_BLACK);
				if (base_check0(arrayCopy0, i, j, rows, cols))
					cout << "●";
				else
					cout << "〇";
				cct_gotoxy(x, y + 1);
			}

		}
		while (1)
		{
			draw_fall(arrayCopy0, rows, cols, choice, arrayCopy, 0);
			for (int i = 0; i < rows; ++i)
			{
				for (int j = 0; j < cols; ++j)
					arrayCopy0[i][j] = arrayCopy[i][j];
			}
			if (base_check1(arrayCopy0, rows, cols))
				continue;
			else
				break;

		}

	}
	else
	{
		for (int i = 0; i < rows; i++)
		{
			for (int j = 0; j < cols; j++)
			{
				draw_ball(i, j, arrayCopy0[i][j], 1);
			}
		}
		int x0, y0;
		cout << endl;
		cct_getxy(x0, y0);
		cct_setcolor(COLOR_BLACK, COLOR_WHITE);// 重置颜色
		for (int i = 0; i < rows; ++i)
		{
			for (int j = 0; j < cols; ++j)
			{
				// 检查并标记可消除项
				if (base_check2(arrayCopy0, directions, i, j, rows, cols))
				{
					draw_ball(i, j, arrayCopy0[i][j], 2);
				}

			}
		}
		cct_setcolor(COLOR_BLACK, COLOR_WHITE);// 重置颜色
		cct_gotoxy(x0, y0);
	}


	int x_9, y_9;
	int num0 = 1;
	int color;
	int i1, j1;
	int i2, j2;
	int count0 = 0;
	cct_enable_mouse();
	cct_setcursor(CURSOR_INVISIBLE);
	while (loop)
	{
		ret = cct_read_keyboard_and_mouse(X, Y, maction, keycode1, keycode2);
		cct_setcolor(COLOR_BLACK, COLOR_WHITE);// 重置颜色
		cct_gotoxy(x9, y9);
		cout << "[当前光标] ";

		if (ret == CCT_MOUSE_EVENT)
		{
			if (X <= 4 * cols && Y <= 2 * rows + 1)
			{
				hang = 'A' + Y / 2 - 1;
				lie = int(X / 4) + 1;
				if ((X % 4 == 2 || X % 4 == 3) && Y % 2 == 0 && Y > 0)
				{
					cout << hang << "行" << lie << "列";

					switch (maction)
					{
						case MOUSE_LEFT_BUTTON_CLICK:
							if (base_check2(arrayCopy, directions, Y / 2 - 1, lie - 1, rows, cols))
							{
								if (num0 > 1)
								{
									cct_gotoxy(x_9, y_9);
									cct_setcolor(color, COLOR_BLACK);
									cout << "◎";
								}
								cct_gotoxy(int(X / 2) * 2, Y);
								x_9 = int(X / 2) * 2;
								y_9 = Y;
								color = arrayCopy[Y / 2 - 1][lie - 1];
								cct_setcolor(color, COLOR_HWHITE);
								cout << "◎";
								Sleep(TIME * 20);
								cct_gotoxy(x9, y9);
								cct_setcolor(COLOR_BLACK, COLOR_WHITE);// 重置颜色
								cout << "当前选择" << hang << "行" << lie << "列";
								Sleep(TIME * 20);
								for (int i = 0; i < rows; ++i)
								{
									for (int j = 0; j < cols; ++j)
										arrayCopy0[i][j] = arrayCopy[i][j];
								}
								if (num0 % 2 == 1)
								{
									i1 = Y / 2 - 1;
									j1 = lie - 1;
								}
								if (num0 % 2 == 0)
								{
									i2 = Y / 2 - 1;
									j2 = lie - 1;

									int tmp0;
									tmp0 = arrayCopy0[i1][j1];
									arrayCopy0[i1][j1] = arrayCopy0[i2][j2];
									arrayCopy0[i2][j2] = tmp0;

									if (base_check0(arrayCopy0, i1, j1, rows, cols) || base_check0(arrayCopy0, i2, j2, rows, cols))
									{
										cct_gotoxy(x9, y9);
										cout << "交换" << char(i1 + 'A') << "行" << j1 + 1 << "列" << "<=>" << char(i2 + 'A') << "行" << j2 + 1 << "列";
										cct_gotoxy(x9, y9 + 1);

										int count = 0;
										if (count == 0)
										{
											for (int i = 0; i < rows; ++i)
											{
												for (int j = 0; j < cols; ++j)
													arrayCopy[i][j] = arrayCopy0[i][j];
											}
										}



										if (base_check1(arrayCopy0, rows, cols))
										{
											for (int i = 0; i < rows; i++)
											{
												for (int j = 0; j < cols; j++)
												{
													x = 4 * j + 2;
													y = 2 * i + 2;
													cct_gotoxy(x, y);
													cct_setcolor(arrayCopy0[i][j], COLOR_BLACK);
													if (base_check0(arrayCopy0, i, j, rows, cols))
														cout << "●";
													else
														cout << "〇";
													cct_gotoxy(x, y + 1);
												}

											}
											while (1)
											{
												score0 = draw_fall(arrayCopy0, rows, cols, choice, arrayCopy, 1);
												score += score0;
												for (int i = 0; i < rows; ++i)
												{
													for (int j = 0; j < cols; ++j)
														arrayCopy0[i][j] = arrayCopy[i][j];
												}
												draw_fall(arrayCopy0, rows, cols, choice, arrayCopy, 1);
												if (!base_check1(arrayCopy0, rows, cols))
													break;

											}

											cct_gotoxy(0, 0);
											cct_setcolor(COLOR_BLACK, COLOR_WHITE);// 重置颜色
											cout << "屏幕：" << d << "行" << 40 << "列";
											cout << "(当前分数：" << score << ")";
											for (int i = 0; i < rows; i++) 
											{
												for (int j = 0; j < cols; j++) 
												{
													if (base_check2(arrayCopy0, directions, i, j, rows, cols)) 
													{
														count0++; // 如果找到满足条件的位置，增加计数
													}
												}
											}

											if (count0 == 0) {
												loop = 0; // 如果没有找到任何满足条件的位置，退出循环
											}
										}
										else
										{
											for (int i = 0; i < rows; i++)
											{
												for (int j = 0; j < cols; j++)
												{
													draw_ball(i, j, arrayCopy0[i][j], 1);
												}
											}
											int x0, y0;
											cout << endl;
											cct_getxy(x0, y0);
											cct_setcolor(COLOR_BLACK, COLOR_WHITE);// 重置颜色
											for (int i = 0; i < rows; ++i)
											{
												for (int j = 0; j < cols; ++j)
												{
													// 检查并标记可消除项
													if (base_check2(arrayCopy0, directions, i, j, rows, cols))
													{
														draw_ball(i, j, arrayCopy0[i][j], 2);
													}
												}
											}
											cct_setcolor(COLOR_BLACK, COLOR_WHITE);// 重置颜色
											cct_gotoxy(x0, y0);
										}
									}
									else
									{
										cct_gotoxy(x9, y9);
										cct_setcolor(COLOR_BLACK, COLOR_WHITE);// 重置颜色
										cout << "不能交换" << char(i1 + 'A') << "行" << j1 + 1 << "列" << "<=>" << char(i2 + 'A') << "行" << j2 + 1 << "列";
										num0 = 0;
									}
								}
								num0++;
							}
							else
							{
								cct_gotoxy(x9, y9);
								cct_setcolor(COLOR_BLACK, COLOR_WHITE);// 重置颜色
								cout << "不能选择" << hang << "行" << lie << "列";
							}
							break;
						case MOUSE_RIGHT_BUTTON_CLICK:
							loop = 0;
							cct_gotoxy(x9, y9);
							break;
					}
				}

				else
				{
					cct_gotoxy(x9, y9);
					cct_setcolor(COLOR_BLACK, COLOR_WHITE);// 重置颜色
					cout << "位置非法";
				}
				cct_setcolor(COLOR_BLACK, COLOR_WHITE);// 重置颜色
				cout << "          ";
				cct_gotoxy(x9, y9);

			}
			else
			{
				cct_setcolor(COLOR_BLACK, COLOR_WHITE);// 重置颜色
				cct_gotoxy(x9, y9);
				cout << "位置非法";
				cout << "        ";
				cct_gotoxy(x9, y9);
			}
		}
	}
	cct_setcolor(COLOR_BLACK, COLOR_WHITE);// 重置颜色
	cct_gotoxy(0, 0);
	cout << "                                             ";
	cct_gotoxy(0, 0);
	cout << "无可消除项,游戏结束!最终分数:" << score << ")";
	cct_gotoxy(x9, y9);
	set_botton(0, 0);
}