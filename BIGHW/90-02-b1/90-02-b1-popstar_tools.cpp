/* 2352018 大数据 刘彦 */
#include <iostream>
#include <cstdlib> 
#include <ctime> 
#include <windows.h>
#include <conio.h>
#include <iomanip>
#include "../include/cmd_console_tools.h"
#include "../include/bighw.h"
#include "90-02-b1-popstar.h"

using namespace std;

/***************************************************************************
  函数名称：star_replace0
  功    能：检查是否可消除的函数
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/

void star_replace0(int mp[MAX_ROWS][MAX_COLS], int flag[MAX_ROWS][MAX_COLS], int mark[MAX_ROWS][MAX_COLS], int row, int col, int x, int y, int target)
{

	if (x < 0 || x >= row || y < 0 || y >= col || flag[x][y] || mp[x][y] != target)
		return;
	flag[x][y] = 1;
	mark[x][y] = 1;

	int dx[] = { 1, -1, 0, 0 };
	int dy[] = { 0, 0, 1, -1 };
	for (int i = 0; i < 4; i++)
	{
		int nx = x + dx[i];
		int ny = y + dy[i];
		star_replace0(mp, flag, mark, row, col, nx, ny, target);
	}

}

/***************************************************************************
  函数名称：print_mark
  功    能：打印当前数组(不同色标识)
  输入参数：
  返 回 值：
  说    明：
***************************************************************************/
void print_mark(int rows, int cols, int array[MIN_ROWS][MAX_ROWS], int mark[MIN_ROWS][MAX_ROWS], int num)
{
	if (num == 0 || num == 3)
		cout << "当前数组(不同色标识):" << endl;
	else if (num == 1)
		cout << "相同值归并后的数组(不同色标识):" << endl;
	else if (num == 2)
		cout << "下落后的数组:" << endl;
	cout << "  | ";
	for (int j = 0; j < cols; ++j)
		cout << " " << j << " ";
	cout << endl;
	cout << "--+-";
	for (int i = 0; i < cols; ++i)
		cout << "---";
	cout << endl;
	for (int i = 0; i < rows; ++i)
	{
		cout << static_cast<char>('A' + i) << " | ";
		for (int j = 0; j < cols; ++j)
		{
			if (num == 0 || num == 1)
			{
				if (mark[i][j] == 1)
				{
					cout << " ";
					cct_setcolor(COLOR_HYELLOW, COLOR_HBLUE);
					cout << array[i][j];
					cct_setcolor(COLOR_BLACK, COLOR_WHITE);
					cout << " ";
				}
				else
					cout << " " << array[i][j] << " ";
			}
			else if (num == 2 || num == 3)
			{
				if (array[i][j] == 0)
				{
					cout << " ";
					cct_setcolor(COLOR_HYELLOW, COLOR_HBLUE);
					cout << array[i][j];
					cct_setcolor(COLOR_BLACK, COLOR_WHITE);
					cout << " ";
				}
				else
					cout << " " << array[i][j] << " ";
			}

		}
		cout << endl;
	}
	cout << endl;
}

/***************************************************************************
  函数名称：star_check
  功    能：检查是否有相同的相邻元素
  输入参数：
  返 回 值：
  说    明：有一个重载函数
***************************************************************************/
int star_check(int mp[MAX_ROWS][MAX_COLS], int row, int col, int x, int y)
{
	int flag[MAX_ROWS][MAX_COLS];
	int mark[MAX_ROWS][MAX_COLS];
	memset(flag, 0, sizeof(flag));
	memset(mark, 0, sizeof(mark));

	int target = mp[x][y];

	star_replace0(mp, flag, mark, row, col, x, y, target);

	int dx[] = { 1, -1, 0, 0 };
	int dy[] = { 0, 0, 1, -1 };
	bool has_adjacent_same = false;

	for (int i = 0; i < 4; i++)
	{
		int nx = x + dx[i];
		int ny = y + dy[i];
		if (nx >= 0 && nx < row && ny >= 0 && ny < col && mark[nx][ny] == 1)
		{
			has_adjacent_same = true;
			break;
		}
	}

	return has_adjacent_same;
}

int star_check(int array[][MAX_COLS], int array_around[][MAX_COLS], int row0, int col0)
{
	array_around[row0][col0] = '*';

	// 定义相邻位置的偏移量
	int directions[4][2] =
	{
		{-1, 0}, // 上
		{0, -1}, // 左
		{0, 1},  // 右
		{1, 0}   // 下
	};

	// 查找相邻元素
	for (int i = 0; i < 4; i++)
	{
		int new_row = row0 + directions[i][0];
		int new_column = col0 + directions[i][1];

		if (new_row >= 0 && new_row < 10 && new_column >= 0 && new_column < 10)
		{
			if (array[row0][col0] == array[new_row][new_column] &&
				array_around[new_row][new_column] != '*')
			{
				array_around[new_row][new_column] = '*';
				star_check(array, array_around, new_row, new_column);
			}
		}
	}

	// 统计标记的元素数量
	int count = 0;
	for (int i = 0; i < 10; i++)
	{
		for (int j = 0; j < 10; j++)
		{
			if (array_around[i][j] == '*')
				count++;
		}
	}

	return (count == 1) ? 0 : 1; // 返回是否有相邻元素
}


/***************************************************************************
	函数名称：move_by_keyboard_and_mouse
	功    能：记录鼠标很键盘移动位置
	输入参数：
	返 回 值：
	说    明：
***************************************************************************/
int move_by_keyboard_and_mouse(int rows, int cols, const int border, int array[][MAX_COLS], int choice, int total)
{
	int ret, maction;
	int keycode1, keycode2;
	int array_around[MAX_ROWS][MAX_COLS] = { 0 };
	int count = -1;
	bool changed = false;
	int chosen = 0;
	int i_last = 0, j_last = 0;
	int i = 0, j = 0;
	int X = 4, Y = 3;
	int end = 0;

	cct_enable_mouse();
	draw_block(0, 0, border, array, rows, cols, -1);
	cct_setcursor(CURSOR_INVISIBLE);

	cct_gotoxy(0, 2 + 2 + rows * (3 + border));
	cout << "箭头键/鼠标移动，回车键/单击左键选择，Q/单击右键结束";

	while (1)
	{
		int i_now = 0, j_now = 0;
		int X_now, Y_now;
		ret = cct_read_keyboard_and_mouse(X_now, Y_now, maction, keycode1, keycode2);

		if (ret == CCT_MOUSE_EVENT)
		{
			location_trans(-1, i_now, j_now, X_now, Y_now, rows, cols, border);
			if (array[i_now][j_now] == 0) 
				i_now = j_now = -1;
			if (array[i][j] == 0) 
				i = j = -1;

			changed = (i != i_now || j != j_now);

			if (maction == MOUSE_ONLY_MOVED)
			{
				if (check_border(X_now, Y_now, border, rows, cols, array))
				{
					if (changed)
					{
						draw_block(i_now, j_now, border, array, rows, cols, -1);
						if (check_border(X, Y, border, rows, cols, array))
							draw_block(i, j, border, array, rows, cols, 1);
					}
					i_last = i_now;
					j_last = j_now;
				}
				else if (changed)
					draw_block(i, j, border, array, rows, cols, 1);
			}
			else if (maction == MOUSE_RIGHT_BUTTON_CLICK)
				end = 1;
			else if (maction == MOUSE_LEFT_BUTTON_CLICK && check_border(X_now, Y_now, border, rows, cols, array))
			{
				draw_block(i_now, j_now, border, array, rows, cols, -1);
				chosen++;
			}

			i = i_now, j = j_now; 
			X = X_now, Y = Y_now;

			if (!(choice == 'F' && !changed))
				print_title(ret, border, rows, cols, i_now, j_now, array);
		}
		else if (ret == CCT_KEYBOARD_EVENT)
		{
			i_now = i_last;
			j_now = j_last;

			if (keycode1 == 224)
			{
				switch (keycode2)
				{
					case KB_ARROW_UP:
						i_now = find_new_position(i_last, -1, rows, array[j_last]);
						break;
					case KB_ARROW_DOWN:
						i_now = find_new_position(i_last, 1, rows, array[j_last]);
						break;
					case KB_ARROW_LEFT:
						j_now = find_new_position(j_last, -1, cols, array[i_last]);
						break;
					case KB_ARROW_RIGHT:
						j_now = find_new_position(j_last, 1, cols, array[i_last]);
						break;
				}
				draw_block(i_now, j_now, border, array, rows, cols, -1);
				draw_block(i_last, j_last, border, array, rows, cols, 1);
			}
			else if (keycode1 == 13)  // 选中
			{
				draw_block(i_last, j_last, border, array, rows, cols, -1);
				chosen++;
				print_title(ret, border, rows, cols, i_last, j_last, array);
				changed = 0;
			}
			else if (keycode1 == 'Q' || keycode1 == 'q')
				end = 1;

			if (!((choice == 'F' && !changed) || chosen))
				print_title(ret, border, rows, cols, i_now, j_now, array);

			i = i_now, j = j_now;//赋值旧的坐标值
			X = X_now, Y = Y_now;
			i_last = i_now;
			j_last = j_now;
		}
		if (chosen)
		{
			if (chosen && (choice == 'D' || choice == 'E'))
				break;
			else if ((choice == 'F' || choice == 'G') && chosen)
			{
				count++;
				if (count == 0) 
				{
					// 显示周围元素
					int is_around = draw_around(rows, cols, border, array, array_around, choice, i_last, j_last);
					if (choice == 'F')
					{
						cct_gotoxy(0, 4 + rows * (3 + border));
						cout << "箭头键/鼠标移动取消当前选择，回车键/单击左键合成";
					}

					if (is_around == 0)
					{
						chosen = 0;
						count = -1; // 进行下一次循环
						continue;
					}
					continue;
				}
				else if (count > 0 && changed)
				{
					// 取消反显
					for (int i = 0; i < rows; i++)
					{
						for (int j = 0; j < cols; j++)
							draw_block(i, j, border, array, rows, cols, 1);
					}
					chosen = 0;
					count = -1;
					changed = 0;
					continue;
				}

				if (chosen == 2)
				{
					// 合成逻辑
					if (choice == 'F') 
					{
						cct_gotoxy(0, 2 + 2 + rows * (3 + border));
						cout << "选择完成，单击左键/回车开始合成                        ";
						wait_for_action();
					}
					pop_together(rows, cols, border, array, i_last, j_last);

					// 下降逻辑
					if (choice == 'F') 
					{
						cct_gotoxy(0, 2 + 2 + rows * (3 + border));
						cout << "合成完成，单击左键/回车开始下降                        ";
						wait_for_action();
					}
					element_fall(array, array_around, rows, cols, 1, border);
					go_right(array, rows, cols, 1, border);

					if (choice == 'F') 
					{
						cct_gotoxy(0, 2 + 2 + rows * (3 + border));
						cct_setcolor(COLOR_BLACK, COLOR_HYELLOW);
						cout << "本次合成结束，按C/单击左键进行新的一次合成             " << endl;
						cct_setcolor();
						wait_for_action('C', true);
						return 0;
					}

					// 判断剩余星星
					int left = 0;
					if (search_finish(array, left, rows, cols) == 0)
					{
						cct_setcolor(COLOR_BLACK, COLOR_HYELLOW);
						int score_gift = (left >= 10) ? 0 : (10 - left) * 180;
						total += score_gift;
						cct_gotoxy(0, 0);
						cout << "奖励得分：" << score_gift << "  " << "总得分：" << total << "       ";
						cct_gotoxy(0, 4 + rows * (3 + border));
						cout << "剩余" << left << "个星星，无可消除项，本关结束！" << endl;
						cct_setcolor();
						cout << "回车进入下一关";
						int xg, yg;
						cct_getxy(xg, yg);
						while (1)
						{
							char ch_g;
							ch_g = _getche();
							if (ch_g == 13)
								break;
							else
							{
								cct_gotoxy(xg, yg);
								putchar(' ');
								cct_gotoxy(xg, yg);
							}
						}
						cout << endl;
						end = 2;
						break;
					}

					// 更新得分
					int count1 = 0;
					int score = 0;
					for (int i = 0; i < rows; ++i)
					{
						for (int j = 0; j < cols; ++j)
						{
							if (array_around[i][j] == '*')
							{
								count1++;
							}
						}
					}
					score = count1 * count1 * 5;
					total += score;
					count1 = 0;
					for (int i = 0; i < 10; i++)
					{
						for (int j = 0; j < 10; j++)
						{
							array_around[i][j] = array[i][j];
						}
					}
					copy_array(array, array_around, rows, cols);
					count = -1;
					chosen = 0;

					cct_gotoxy(0, 0);
					cout << "本次得分：" << score << "  " << "总分：" << total << "         ";
				}

			}
		}


		if (end)
			break;
	}
	cct_disable_mouse();
	cct_setcursor(CURSOR_VISIBLE_NORMAL);
	return end;
}




/***************************************************************************
	函数名称：find_new_position
	功    能：查找在给定行中的新位置
	输入参数：
	返 回 值：
	说    明：
***************************************************************************/
int find_new_position(int start, int direction, int cols, int rows[])
{
	int j_now = start;
	if (direction < 0)
	{
		for (int j_left = start - 1; j_left >= 0; j_left--)
		{
			if (rows[j_left] != 0)
			{
				j_now = j_left;
				break;
			}
		}
		if (j_now == start)
		{
			for (int j_1 = cols - 1; j_1 >= start; j_1--)
			{
				if (rows[j_1] != 0)
				{
					j_now = j_1;
					break;
				}
			}
		}
	}
	else {
		for (int j_right = start + 1; j_right < cols; j_right++)
		{
			if (rows[j_right] != 0)
			{
				j_now = j_right;
				break;
			}
		}
		if (j_now == start) {
			for (int j_1 = 0; j_1 <= start; j_1++)
			{
				if (rows[j_1] != 0)
				{
					j_now = j_1;
					break;
				}
			}
		}
	}
	return j_now;
}

/***************************************************************************
	函数名称：print_title
	功    能：显示当前鼠标位置/键盘位置/提示信息等
	输入参数：
	返 回 值：
	说    明：
***************************************************************************/
void print_title(int ret, int border, int rows, int cols, int i, int j, int array[][MAX_COLS])
{
	int X, Y;
	location_trans(1, i, j, X, Y, rows, cols, border);

	// 转到下方状态栏进行打印
	cct_gotoxy(0, 2 + 2 + rows * (3 + border));

	bool valid_position = check_border(X, Y, border, rows, cols, array);

	// 打印信息
	if (ret == CCT_MOUSE_EVENT || (ret == CCT_KEYBOARD_EVENT && border == 0))
	{
		if (valid_position) {
			if (ret == CCT_MOUSE_EVENT)
				cout << "[当前鼠标] " << (char)(i + 'A') << "行" << (char)(j + '0') << "列                                     ";
			else
				cout << "[当前键盘] " << (char)(i + 'A') << "行" << (char)(j + '0') << "列                                     ";
		}
		else {
			if (ret == CCT_MOUSE_EVENT)
				cout << "[当前鼠标] 位置非法                                                    ";
			else
				cout << "[当前键盘] 位置非法                                                    ";
		}
	}
}

/***************************************************************************
	函数名称：check_border
	功    能：根据不同的border判断是否在合法区域
	输入参数：
	返 回 值：
	说    明：
***************************************************************************/
bool check_border(int X, int Y, int border, int rows, int cols, int array[][MAX_COLS])
{
	// 计算合法区域的范围
	int y_min = 3;
	int y_max = 3 + rows * (3 + border);
	int x_min = 4;
	int x_max = 4 + (6 + border * 2) * cols;

	// 检查是否在基本范围内
	if (Y < y_min || Y >= y_max || X < x_min || X >= x_max)
		return false;


	// 如果 border 为 1，进行额外的检查
	if (border == 1)
		if (!((Y - 3) % 4 <= 2 && (X - 4) % 8 <= 5))
			return false;

	// 转换坐标并检查数组值
	int i, j;
	location_trans(-1, i, j, X, Y, rows, cols, border);
	return array[i][j] != 0; // 如果值不为0，返回 true
}


/***************************************************************************
	函数名称：draw_map
	功    能：显示界面全局图形
	输入参数：
	返 回 值：
	说    明：
***************************************************************************/
void draw_map(int rows, int cols, const int border, int array[][MAX_COLS], int choice)
{
	int if_g = 1;
	int total = 0;//总得分
	while (if_g)
	{
		if (choice != 'G')
			if_g = 0;
		//根据行列数设置cmd窗口宽度高度
		fill_array(array, rows, cols, 2);
		cct_setconsoleborder((6 + border * 2) * cols + 8, 3 * (rows + border * 2) + 10, -1, -1);
		cct_cls();
		//显示外部边框线
		draw_border(rows, cols, border, choice, 2);
		//画色块
		for (int i = 0; i < rows; i++)
		{
			for (int j = 0; j < cols; j++)
				draw_block(i, j, border, array, rows, cols, 1);
		}
		//显示上方状态栏
		int columns, lines, a, b;
		cct_getconsoleborder(columns, lines, a, b);
		cct_gotoxy(0, 0);
		cout << "屏幕当前设置为：" << lines << "行" << columns << "列" << endl;

		int end = 0;
		end = move_by_keyboard_and_mouse(rows, cols, border, array, choice, total);
		if (end == 1)
			break;
	}
}


/***************************************************************************
	函数名称：wait_for_action
	功    能：等待用户操作的函数
	输入参数：
	返 回 值：
	说    明：
***************************************************************************/
void wait_for_action(char key, bool mouse_click)
{
	while (1)
	{
		int MX, MY, maction, keycode1, keycode2, ret;
		ret = cct_read_keyboard_and_mouse(MX, MY, maction, keycode1, keycode2);
		if ((mouse_click && ret == CCT_MOUSE_EVENT && maction == MOUSE_LEFT_BUTTON_CLICK) || (key && ret == CCT_KEYBOARD_EVENT && (keycode1 == key || keycode1 == (key - 32))))
			break;
		if (!mouse_click && ret == CCT_KEYBOARD_EVENT && keycode1 == 13)
			break;
	}
}

/***************************************************************************
	函数名称：go_right
	功    能：查看有无全零，将全零移动至最右侧
	返 回 值：
	说    明：
***************************************************************************/
void go_right(int array[][MAX_COLS], int rows, int cols, int have_block, int choice)
{
	int count = 0; // 记录已移动的全零列的数量

	for (int j = 0; j < cols - count; j++)
	{
		bool is_all_zero = true;

		// 检查列是否全为零
		for (int i = 0; i < rows; i++)
		{
			if (array[i][j] != 0)
			{
				is_all_zero = false;
				break;
			}
		}

		if (is_all_zero)
		{
			// 记录全零列的位置
			int col_to_move = j;
			count++;
			// 将全零列移动到最右侧
			move_zero_column_to_right(array, rows, cols, col_to_move, have_block, choice);
			j--; // 重新检查当前列的位置
		}
	}
}

/***************************************************************************
	函数名称：go_right
	功    能：移动指定列到最右侧的函数
	返 回 值：
	说    明：
***************************************************************************/
void move_zero_column_to_right(int array[MAX_ROWS][MAX_COLS], int rows, int cols, int col_to_move, int have_block, int choice)
{
	for (int m = 0; m < rows; m++)
	{
		for (int n = col_to_move; n < cols - 1; n++)
		{
			array[m][n] = array[m][n + 1];
			array[m][n + 1] = 0;
			if (array[m][n] != 0 && have_block == 1) 
			{
				draw_block(m, n, choice, array, rows, cols, 1);
				Sleep(10);
				draw_block(m, n + 1, choice, array, rows, cols, 0);
				Sleep(10);
			}

		}
	}
}

/***************************************************************************
	函数名称：search_finish
	功    能：看不是0的元素->是否还有可消灭的星星
	返 回 值：0/1
	说    明：null
***************************************************************************/
int search_finish(int array[MAX_ROWS][MAX_COLS], int& left, int row, int col)
{
	int is_have = 0;
	for (int i = 0; i < row; i++) 
	{
		for (int j = 0; j < col; j++)
		{
			if (array[i][j] != 0) 
			{
				int array_around[MAX_ROWS][MAX_COLS] = { 0 };
				int is_have_have = 0;
				is_have_have = star_check(array, row, col, i, j);
				if (is_have_have == 1)
					is_have = 1;
				left++;
			}
		}
	}
	if (is_have)
		return 1;
	else
		return 0;

}